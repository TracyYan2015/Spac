# 1.Checker.py
__author__ = 'hekk'

import logging
logging.basicConfig(level=logging.DEBUG)
import copy
import random
import threading
import re


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
            return (self.end-interval.begin)*(self.begin-interval.end) < 0

class Checker(threading.Thread):
    # model: DTMC/CTMC models represented as an instance of ModulesFile 
    # ltl: a CSL/PCTL formula's ltl part
    # a, b: Alpha parameter and beta parameter of beta distribution.  
    # c, d: Confidence parameter and approximate parameter.  
    # duration: number of seconds to determine the sample path length. 
    # In DTMC cases, it just represents the number of steps
    def __init__(self, model, ltl, a=1, b=1, c=0.8, d=0.1, duration=1.0): 
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

    def __max_state_of(self, states):
        # print states
        if states is None or len(states) == 0:
            return None
        if isinstance(states[0], state):
            return max(states, key=lambda x: x.id)

    def __min_state_of(self, states):
        if states is None or len(states) == 0:
            return None
        if isinstance(states[0], state):
            return min(states, key=lambda x: x.id)

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


    # path: list of states(NOT list of ap of states!!!)
    # state_id: the index of state in path, NOT the state'id
    # return: the key state object
    def __get_key_state(self, path, state_id, ltl, ltl_root):
        ltl_root_symbol = ltl[ltl_root]
        if ltl_root_symbol == '&':
            res_states = self.__rverify(ltl_root, [p.ap for p in path])
            if state_id in res_states:
                # path[state_id] satisfies y1&y2
                return self.__max_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+1), self.__get_key_state(path, state_id, ltl, ltl_root*2+2)])
            else:
                # compute the states that satisfy y1
                res_left_states = self.__rverify(ltl_root*2+1, [p.ap for p in path])
                # compute the states that satisfy y2
                res_right_states = self.__rverify(ltl_root*2+2, [p.ap for p in path])
                
                # y1 satisfied and y2 not satisfied
                if state_id in res_left_states and state_id not in res_right_states:
                    return self.__get_key_state(path, state_id, ltl, ltl_root*2+2)
                elif state_id not in res_left_states and state_id in res_right_states:
                    return self.__get_key_state(path, state_id, ltl, ltl_root*2+1)
                else:
                    return self.__min_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+1), self.__get_key_state(path, state_id, ltl, ltl_root*2+2)])
        elif ltl_root_symbol == '|':
            res_states = self.__rverify(ltl_root, [p.ap for p in path])
            if state_id in res_states:
                # path[state_id] satisfied y1|y2
                # compute the states that satisfy y1
                res_left_states = self.__rverify(ltl_root*2+1, [p.ap for p in path])
                # compute the states that satisfy y2
                res_right_states = self.__rverify(ltl_root*2+2, [p.ap for p in path])
                if state_id in res_left_states and state_id not in res_right_states:
                    return self.__get_key_state(path, state_id, ltl, ltl_root*2+1)
                elif state_id not in res_left_states and state_id in res_right_states:
                    return self.__get_key_state(path, state_id, ltl, ltl_root*2+2)
                else:
                    return self.__min_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+1), self.__get_key_state(path, state_id, ltl, ltl_root*2+2)])
            else:
                # y1|y2 not satisfied
                return self.__max_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+1), self.__get_key_state(path, state_id, ltl, ltl_root*2+2)])
        elif ltl_root_symbol == 'X':
            return self.__get_key_state(path, state_id+1, ltl, ltl_root+1)
        elif ltl_root_symbol == '!':
            return self.__get_key_state(path, state_id+1, ltl, ltl_root+1)
        # add steps restriction to until check
        # change 'U' to "Usteps" e.g. "U10"
        elif ltl_root_symbol[0] == 'U':
            try:
                steps = int(ltl_root_symbol[1:])
            except Exception as e:
                print "steps invalid "
            res_states = self.__rverify(ltl_root, [p.ap for p in path])
            if state_id in res_states:
                # y1Uy2 satisfied
                res_right = self.__rverify(ltl_root*2+2, [p.ap for p in path])
                # print "states that satisfy y2"
                # print res_right
                # get the minimum id of state that satisfies y2(the right formula)
                # list of states that satisfied y2
                right_min_id = min(res_right)
                # print right_min_id
                test_ids = range(right_min_id)
                # print test_ids
                state_y1 = self.__max_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+1) for state_id in test_ids])
                state_y2 = self.__get_key_state(path, right_min_id, ltl, ltl_root*2+2)
                # state_y2 = self.__max_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+2) for state_id in test_ids])
                return self.__max_state_of([state_y1, state_y2])
            else:   
                # y1Uy2 not satisfied
                res_left_states = self.__rverify(ltl_root*2+1, [p.ap for p in path])
                res_right_states = self.__rverify(ltl_root*2+2, [p.ap for p in path])
                # all_state_ids = set([s.id for s in path])
                # state's id that not satisfy y1
                not_res_left_states = set()
                # get the index of states that not satisfy left child property
                indexes_left = set(range(len(path))) - set(res_left_states)
                # get the index of states that not satisfy right child property
                indexes_right = set(range(len(path))) - set(res_right_states)

                # the min state's id that y1 and y2 not satisfied at the same time
                # print "states's index that not satisfied y1 and y2: "
                # print str(indexes_left)
                # print str(indexes_right)
                # states's index that not satisfy y1 and y2
                sidxy1_y2 = indexes_left & indexes_right
                if len(sidxy1_y2) == 0:
                    print "return the whole path as the prefix"
                    return path[len(path)-1]
                id1 = min(sidxy1_y2) # here's where most bugs happen.
                print "min_id: " + str(id1)
                test_ids = range([p.id for p in path].index(id1))
                print "test_ids: " + str(test_ids)
                tmp1 = self.__max_state_of([self.__get_key_state(path, state_id, ltl, ltl_root*2+2) for state_id in test_ids])
                return self.__max_state_of([self.__get_key_state(path, state_id-1, ltl, ltl_root*2+1), self.__get_key_state(path, state_id-1, ltl, ltl_root*2+2), tmp1])
        else:
            # ltl is AP
            if state_id >= len(path) or state_id < 0:
                print "IndexError: " + str(state_id)
            return path[state_id]

    # returned (result, path e.g. list of Step instance)
    # using cachedPrefixes to check the path's checking result beforehand
    def getRandomPath(self):
        return self.modulesFile.genRandomPath(self.duration, self.cachedPrefixes)

    def get_decidable_prefix(self, path, state_id, ltl, ltl_root):
        print "result of get_key_state: "
        key_state = self.__get_key_state(path, state_id, ltl, ltl_root)
        print key_state
        # using the id of keystate object to get the prefix
        idx = [id(p) for p in path].index(id(key_state))
        return path[0:idx+1]

    # ltl verification method
    # return: boolean
    # path: list of Step instance
    def verify(self, path):
        logging.info('Verification begins.')
        logging.info('ltl: %s' % str(self.ltl))
        satisfiedStates = self._rverify(path, 0)
        return 0 in [state.stateId for state in satisfiedStates]

    # ltlRoot: current ltl symbol's index in ltl
    # return: set of State instance's id that satisfy ltl
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
            return set([step.stateId for step in path])-lstates
        elif ltl[ltlRoot][0] == 'U':
            if len(ltl[ltlRoot]) > 0:
                nums = re.findall(ur'\d+', ltl[ltlRoot])
                if len(nums) != 2:
                    logging.error("Time interval for until formula must contains two values: begin and end.")
                    return None
            timeInterval = map(lambda x: int(x), nums)
            timeInterval = Interval(*timeInterval)
            if timeInterval[0] > timeInterval[1]:
                logging.error("invalid ltl until time interval")
                return set()

            lstates = self._rverify(path, ltlRoot*2+1)
            logging.info('left formula finished.')
            logging.info('lstates size: %s' % str(len(lstates)))
            rstates = self._rverify(path, ltlRoot*2+2)
            logging.info('right formula finished.')
            logging.info('rstates size: %s' % str(len(rstates)))
            return self._checkU(lstates, rstates, path, timeInterval)
        elif ltl[ltlRoot] == 'X':
            lstates = self._rverify(path, ltlRoot*2+1)
            return self._checkX(lstates)
        elif ltl[ltlRoot] == 'T':
            # the True situation
            return set([step.stateId for step in path])
            # return set([stateTuple[0] for stateTuple in path])
        else:
            ap = ltl[ltlRoot]
            return self._checkAP(path, ap)


    # check y1 U(Interval) y2
    # lstates: states that satisfy y1
    # rstates: states that satisfy y2
    # path: list of Step instance
    # PAY ATTENTION THAT THE DEFINITION OF Step class has changed!
    # timeInterval: the interval parameter of until formula
    # return: states's ids that satisfy y1 U(Interval) y2
    def _checkU(self, lstates, rstates, path, timeInterval):
        # the idea here...
        # if there's state i that satisfy y2
        # and any states that before i satisfy y1
        # then add both i and j(<i) to states.
        logging.info('Enter _checkU')
        result = set()
        started = False

        # TODO traverse throught the path from the beginning?
        for index,step in enumerate(path[::-1]):
            stateId = step.stateId
            if stateId in rstates:
                # check if state is within timeInterval
                stateBeginTime = step.passedTime
                stateEndTime = step.passedTime + step.holdingTime
                interval = Interval(stateBeginTime, stateEndTime)
                if interval.interleaveWith(timeInterval):
                    result.add(stateId)
                    started = True
            elif stateId in lstates and started:
                result.add(stateId)
            else:
                started = False
        return result

    def _checkX(self, lstates):
        result = set()
        for stateId in lstates:
            if stateId >= 1:
                result.add(stateId)
        return result

    def _checkAP(self, path, ap):
        result = set()
        for stateId, apSet in zip([step.stateId for step in path], [step.apSet for step in path]):
            if ap in apSet:
                result.add(stateId)
        return result


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

        postex = s.postEx(n, x)
        l = postex-s.d
        h = postex+s.d
        l = 0 if l<0 else l
        h = 1 if h>1 else h

        return l,h

    #Begin to check.
    def run(self):
        msg = None
        if self.checkingType == 0:
            self.is_satisfy = self.mc1()
            if self.is_satisfy:
                msg = "The model satisfies the LTL."
            else:
                msg = "The model does not satisfy the LTL."
        else:
            self.lower,self.upper =  self.mc2()
            msg = "The probability is ["+str(self.lower)+","+str(self.upper)+"]."



