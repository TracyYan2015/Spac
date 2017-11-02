# 1.Checker.py
__author__ = 'hekk'

import logging
logging.basicConfig(level=logging.DEBUG)
import threading
import re
import bisect


# class represent an interval in DTMC/CTMC
# using -1 as the end to represent the unbound situation
class Interval:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        self.bounded = begin*end >= 0

    def __getitem__(self, n):
        if n == 0:
            return self.begin
        else:
            return self.end

    def interleaveWith(self, interval):
        if not self.bounded and not interval.bounded:
            return True
        elif self.bounded and not interval.bounded:
            return self.end > interval.begin
        elif not self.bounded and interval.bounded:
            return interval.end > self.begin
        else:
            return (self.end-interval.begin)*(self.begin-interval.end) <= 0

    # check whether the state of the step in the this Interval
    def contains(self, step):
        if not self.bounded:
             return step.passedTime >= self.begin
        else:
            return step.passedTime < self.end and step.passedTime >= self.begin


class Checker(threading.Thread):
    class CheckingType:
        QUANTATIVE, QUALITATIVE = range(2)
    # model: DTMC/CTMC models represented as an instance of ModulesFile
    # ltl: a CSL/PCTL formula's ltl part
    # a, b: Alpha parameter and beta parameter of beta distribution.
    # c, d: Confidence parameter and approximate parameter.
    # duration: number of seconds to determine the sample path length.
    # In DTMC cases, it just represents the number of steps
    def __init__(self, model=None, ltl=None, a=1, b=1, c=0.8, d=0.05, duration=1.0, checkingType=None):
        threading.Thread.__init__(self)
        self.model = model
        self.ltl = ltl
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.lower = 0.0
        self.upper = 0.0
        self.is_satisfy = False
        
        self.cachedPrefixes = dict()
        self.checkingType = checkingType
        self.duration = duration

    #Get upper-bound of variance
    def __getVar_m(self, n, a, b):
        x = (n+b-a)/2.0
        p = (n+a+b)*(n+a+b)*(n+a+b+1.0)
        return (x+a)*(n-x+b)/p

    #Get Variance of Beta distribution
    def __getVar(self, n, x, a, b):
        p = n+a+b
        d1 = (x+a)*(n-x+b)
        d2 = p*p*(p+1.0)
        return d1/d2


    def getSampleSize(self):
        return int(1.0/((1-self.c)*4*self.d*self.d)-self.a-self.b-1)


    # path: list of Step instance
    # step: current steps(which contains current state)
    # return: the state_id (which stores in Step instance) of the key state
    def _get_key_state(self, path, step, ltl_root):
        ltl = self.ltl
        ltl_root_symbol = ltl[ltl_root]
        state_id = step.stateId
        if ltl_root_symbol == '&':
            if self.verify(path):
                return max([self._get_key_state(path, step, ltl_root*2+1),self._get_key_state(path, step, ltl_root*2+2)],
                    key=lambda s: s.stateId)
            else:
                l_states = self._rverify(path, ltl_root*2+1)
                r_states = self._rverify(path, ltl_root*2+2)

                if step in l_states and step not in r_states:
                    return self._get_key_state(path, step, ltl_root*2+2)
                elif step not in l_states and step in r_states:
                    return self._get_key_state(path, step, ltl_root*2+1)
                else:
                    return min([self._get_key_state(path, step, ltl_root*2+1), self._get_key_state(path, step, ltl_root*2+2)],
                        key=lambda s: s.stateId)
        elif ltl_root_symbol == '|':
            if self.verify(path):
                l_states = self._rverify(path, ltl_root*2+1)
                r_states = self._rverify(path, ltl_root*2+2)
                if step in l_states and step not in r_states:
                    return self._get_key_state(path, step, ltl_root*2+1)
                elif step not in l_states and step in r_states:
                    return self._get_key_state(path, step, ltl_root*2+2)
                else:
                    return min([self._get_key_state(path, step, ltl_root*2+1), self._get_key_state(path, step, ltl_root*2+2)],
                        key=lambda s:s.stateId)
            else:
                return max([self._get_key_state(path, step, ltl_root*2+1), self._get_key_state(path, step, ltl_root*2+2)],
                    key=lambda s:s.stateId)
        elif ltl_root_symbol == 'X':
            next_step = path[bisect.bisect([s.stateId for s in path], step.stateId)]
            return self._get_key_state(path, next_step, ltl_root*2+1)
        elif ltl_root_symbol == '!':
            return self._get_key_state(path, step, ltl_root*2+1)
        elif ltl_root_symbol[0] == 'U':
            interval = Interval(*[int(n) for n in re.findall(r'\d+', ltl_root_symbol)])
            if self.verify(path):
                r_states = self._rverify(path, ltl_root*2+2)
                return min([s for s in r_states if interval.contains(s)],key=lambda s:s.stateId)
            else:
                l_states = self._rverify(path, ltl_root*2+1)
                temp = set(path) - l_states
                if not temp:
                    # all states satisfy y1, return last state as the key state
                    return path[-1]
                else:
                    return min(temp, key=lambda s:s.stateId)
        else:
            # AP
            if state_id >= len(path) or state_id < 0:
                logging("IndexError: " + str(state_id))
            return step


    # returned (result, path e.g. list of Step instance)
    # using cachedPrefixes to check the path's checking result beforehand
    def getRandomPath(self):
        return self.model.genRandomPath(self.duration, self.cachedPrefixes)

    # path: list of Step
    # step: current Step instance
    # ltl: ltl formula
    # ltl_root: current ltl symbol in ltl
    # return: list of Step instance
    def _get_decidable_prefix(self, path, step, ltl_root):
        key_step = self._get_key_state(path, step, ltl_root)
        key_step_idx = bisect.bisect([s.stateId for s in path], key_step.stateId-1)
        return path[0:key_step_idx+1] # [)


    # ltl verification method
    # return: boolean
    # path: list of Step instance
    def verify(self, path):
        satisfiedSteps = self._rverify(path, 0)
        return 0 in map(lambda step: step.stateId, satisfiedSteps)


    # path: list of Step instance
    # ltlRoot: current ltl symbol's index in ltl
    # return: set of Step instance whose corresponding State satisfy the ltl formula
    # if no state satisfy ltl, return empty set()
    def _rverify(self, path, ltlRoot):
        ltl = self.ltl
        if ltlRoot > len(ltl):
            return set()
        elif ltl[ltlRoot] == '&':  #conjunction
            lstates = self._rverify(path, ltlRoot*2+1)
            rstates = self._rverify(path, ltlRoot*2+2)
            return lstates & rstates
        elif ltl[ltlRoot] == '|': #disjunction
            lstates = self._rverify(path, ltlRoot*2+1)
            rstates = self._rverify(path, ltlRoot*2+2)
            return lstates | rstates
        elif ltl[ltlRoot] == '!':
            lstates = self._rverify(path, ltlRoot*2+1)
            return set([step for step in path])-lstates
        elif ltl[ltlRoot][0] == 'U':
            if len(ltl[ltlRoot]) > 0:
                nums = re.findall(r'\d+', ltl[ltlRoot])
                if len(nums) != 2:
                    logging.error("Time interval for until formula must contains two values: begin and end.")
                    return None
            timeInterval = Interval(*[int(n) for n in nums])
            if timeInterval[0] > timeInterval[1]:
                logging.error("invalid ltl until time interval")
                return set()

            lstates = self._rverify(path, ltlRoot*2+1)
            rstates = self._rverify(path, ltlRoot*2+2)
            return self._checkU(lstates, rstates, path, timeInterval)
        elif ltl[ltlRoot] == 'X':
            lstates = self._rverify(path, ltlRoot*2+1)
            return self._checkX(path, lstates)
        elif ltl[ltlRoot] == 'T':
            return set(path)
        else:
            ap = ltl[ltlRoot]
            return self._checkAP(path, ap)


    # check y1 U(Interval) y2
    # lstates: step instance that satisfy y1
    # rstates: step instance that satisfy y2
    # path: list of Step instance
    # PAY ATTENTION THAT THE DEFINITION OF Step class has changed!
    # timeInterval: the interval parameter of until formula
    # return: step instance that satisfy y1 U(Interval) y2
    def _checkU(self, lstates, rstates, path, timeInterval):
        # the idea here...
        # if there's state i that satisfy y2
        # and any states that before i satisfy y1
        # then add both i and j(<i) to states.
        result = set()
        started = False

        # TODO traverse throught the path from the beginning?
        for index,step in enumerate(path[::-1]):
            if step in rstates:
                # check if state is within timeInterval
                stateBeginTime = step.passedTime
                stateEndTime = step.passedTime + step.holdingTime
                interval = Interval(stateBeginTime, stateEndTime)
                if interval.interleaveWith(timeInterval):
                    result.add(step)
                    started = True
            elif step in lstates and started:
                result.add(step)
            else:
                started = False
        return result

    # lstates: step instances that satisfy y in Xy
    def _checkX(self, path, lstates):
        result = set()
        lstates = filter(lambda s:s.stateId >= 1, lstates)
        stateIds = [step.stateId for step in path]
        for s in lstates:
            result.add(path[bisect.bisect(stateIds, s.stateId)-2])
        return result

    def _checkAP(self, path, ap):
        return set([s for s in path if ap in s.apSet])


    #Get the expectation value of posterior distribution.
    def postEx(self, n, x):
        return (self.a+x)/(n+self.a+self.b)

    #Get confidence of estimating.
    def con(self, a, b, n, x, ex, p):
        tEX = (a+x)/(n+a+b)
        tVar = self.__getVar(n, x, a, b)
        td = abs(p-tEX)
        if td == 0:
            con = -1
        else:
            con = (1.0-tVar/(td*td))
        return con

    #Check whether property holds
    def mc1(self):
        s = self

        # event = self.FinishEventClass(output='Starting to verify...')
        # wx.PostEvent(self.frame, event)

        sz = int(s.getSampleSize(s.a, s.b, s.c, s.d))
        # event = self.FinishEventClass(output='The upper bound of sample size is '+str(sz))
        # wx.PostEvent(self.frame, event)

        # event = self.FinishEventClass(output='Verifying...')
        # wx.PostEvent(self.frame, event)

        x,n = 0.0, 0.0
        postex = 0.0
        for i in range(sz):
            satisfied,path = s.getRandomPath(self.decided_prefixes)
            # print "path:"
            # print "path:"
            # for p in path:
              #  print p
            # n += 1
            n += 1
            if s.verify([p.ap for p in path], s.ltl, s.pts):
                x += 1
            postex = s.postEx(s.a, s.b, n, x)
            confidence=s.con(s.a, s.b, n, x, postex, s.p)

            if confidence >= s.c:

                # event = self.FinishEventClass(output=str(int(n))+' samples are verified.')
                # wx.PostEvent(self.frame, event)

                if postex > s.p :
                    if s.op == '>':
                        return True
                    else:
                        return False
                elif postex < s.p :
                    if s.op == '<':
                        return True
                    else:
                        return False
                elif postex == s.p :
                    if s.op == '=':
                        return True
                    else:
                        return False

        if postex == s.p and s.op == '=':
            return True
        else:
            return False

    #Estiamte the probability of property holding
    def mc2(self):
        sz = self.getSampleSize()
        logging.info('Sampling size: %s' % sz)
        x,n = 0,0
        for i in range(sz):
            satisfied, path = self.getRandomPath()
            n += 1
            if not satisfied:
                verified = self.verify(path)
                if verified:
                    x += 1
            logging.info('Verified result: %s' % str(verified))

        postex = self.postEx(n, x)
        l = postex-self.d
        h = postex+self.d
        l = 0 if l<0 else l
        h = 1 if h>1 else h

        return l,h

    #Begin to check.
    def run(self):
        msg = None
        if self.checkingType == Checker.CheckingType.QUALITATIVE:
            self.is_satisfy = self.mc1()
            if self.is_satisfy:
                msg = "The model satisfies the LTL."
            else:
                msg = "The model does not satisfy the LTL."
        else:
            return self.mc2()


