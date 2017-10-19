# 1.Checker.py
__author__ = 'hekk'

import random
import threading
# import wx
# import wx.lib.newevent

#The state of adjacent list.
class state():
    def __init__(self, sid, postStates, ap):
        self.id = sid
        self.postStates = postStates
        self.ap = ap

    def __str__(self): 
        if self.ap is not None: 
            return "id: " + str(self.id) + " ap:" + ''.join(self.ap) 
    def __len__(self): 
        return len(self.ap) 

class Checker(threading.Thread): 
    # a, b: Alpha parameter and beta parameter of beta distribution.  
    # c, d: Confidence parameter and approximate parameter.  
    # k: Length of random path.  
    # p: Probability threshold of the proposition.  
    # op: Operator of the proposition.  
    # type: Choose qualitative or quantitative algorithm 
    # frame: window's handler 
    def __init__(self, pts, ltl, a, b, c, d, k, p, op , type, frame=None, FinishEventClass=None): 
        threading.Thread.__init__(self)
        self.pts = pts
        self.ltl = ltl
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.k = k
        self.p = p
        self.op = op
        self.type = type
        self.lower = 0.0
        self.upper = 0.0
        self.is_satisfy = False
        self.frame = frame
        self.decided_prefixes = {}
        # self.FinishEventClass = FinishEventClass

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

    #TODO overflow
    #Get Max sample size
    def getMaxSize(self, a, b, c, d):
        s = self
        n = 1
        variance = (1-c)*d*d 
        if (variance == 0): return 0

        res = s.__getVar_m(n, a, b)
        while res >= variance:
            n = n*2
            res = s.__getVar_m(n, a, b)

        low = n/2
        high = n
        while low <= high:
            mid = (low+high)/2
            tvar = s.__getVar_m(mid, a, b)
            if variance == tvar:
                return mid
            elif tvar < variance:
                high = mid-1
            else:
                low = mid+1
        return low


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

    #Get a random path
    def getPath(self, decided_prefixes):
        pts = self.pts
        k = self.k
        satisfied = None
        import copy
        path = list()
        sid = 1 #stateid
        # insert copy of state's object into path
        # to make all elements in path have distinct ids
        path.append(copy.copy(pts[sid]))

        for i in range(k):
            rnd = random.random()
            sum = 0.0

            if (len(pts[sid].postStates) == 0): return path

            for j in range(len(pts[sid].postStates)):
                try:
                    sum += pts[sid].postStates[j][1]
                except Exception as e:
                    print "exception happens: " + str(sid)
                    raise e
                
                if(sum >= rnd):
                    sid = pts[sid].postStates[j][0]
                    break
            path.append(copy.copy(pts[sid]))
            # check if p has been in decided_prefixes
            key = ''.join([str(p.id) for p in path])
            if decided_prefixes.has_key(key):
                satisfied = decided_prefixes[key]
                return (path, satisfied)
        # print "path's length: "+str(len(path))
        return (path, satisfied)
    # def getPath(self):
    #     s = self
    #     path = list()
    #     sid = 1 #stateid
    #     path.append(self.pts[sid].ap)

    #     for i in range(self.k):
    #         rnd = random.random()
    #         sum = 0.0

    #         if (len(self.pts[sid].postStates) == 0): return path

    #         for j in range(len(self.pts[sid].postStates)):
    #             sum += self.pts[sid].postStates[j][1]
    #             if(sum >= rnd):
    #                 sid = self.pts[sid].postStates[j][0]
    #                 break
    #         path.append(self.pts[sid].ap)

    #     return path


    def get_decidable_prefix(self, path, state_id, ltl, ltl_root):
        print "result of get_key_state: "
        key_state = self.__get_key_state(path, state_id, ltl, ltl_root)
        print key_state
        # using the id of keystate object to get the prefix
        idx = [id(p) for p in path].index(id(key_state))
        return path[0:idx+1]

    #Portal of check algorithm
    def verify(self, path, ltl, pts):
        min_rstate = -1
        states = self.__rverify(0, path)
        if None is states:
            return False
        elif 0 in states:
            return True
        else:
            return False

    #Check until
    # def checkU(self, lstates, rstates, path):
    #     if rstates == None:
    #         return None

    #     i = len(path)-1
    #     states = set()
    #     started = False

    #     while i >= 0:
    #         if i in rstates:
    #             started = True
    #             states.add(i)
    #         elif i in lstates and started:
    #             states.add(i)
    #         else:
    #             started = False
    #         i -= 1
    #     return states

    # lstates, rstates: set of states that satisfy y1 and y2
    def checkU(self, lstates, rstates, path): 
        # print "checkU..." 
        # print "lstates:" 
        # print str(lstates) 
        # print "rstates:" 
        # print str(rstates) 
        # print "path:" 
        # for p in path: 
        #     print p 
        # print "steps:" + str(steps) 
        if rstates == None: 
            return None 
        i = len(path)-1 
        states = set() 
        started = False 
        # the idea here...  
        # if there's state i that satisfy y2 
        # and any states that before i satisfy y1 
        # then add both i and j(<i) to states.  
        # min_rstate: the minimum index of state in path that satisfy y2 
        min_rstate = -1 
        if len(rstates) > 0: 
            min_rstate = max(rstates)
        else:
            # There's no states that satisfy y2
            # thus no states satisfy y1 U y2 
            return (set(), min_rstate)
        while i >= 0:
            if i in rstates:
                if min_rstate > i:
                    min_rstate = i
                started = True
                states.add(i)
            elif i in lstates and started:
                states.add(i)
            else:
                started = False
            i -= 1
        return (states, min_rstate)


    #Check next
    def checkX(self, lstates, path):
        if lstates==None:
            return None

        l = len(path)-1
        states = set()
        for sid in lstates:
            if(sid-1 >= 0):
                states.add(sid-1)
        return states

    #Check AP
    # def verifyAP(self, root, path, ltl):
    #     if(root > len(ltl)-1):
    #         return None
    #     ap = ltl[root]
    #     i = 0  #order in path
    #     states = set()
    #     while i <= len(path)-1:
    #         if ap in path[i]:
    #             states.add(i)   #because stat no from1
    #         i += 1
    #     return states

    # verifyAP returns empty set or set of states' id that contains the ltl[root]
    # but if root is out of ltl's indexes, then return None
    def verifyAP(self, root, path, ltl):
        if(root > len(ltl)-1):
            return None
        ap = ltl[root]
        i = 0  #order in path
        states = set()
        while i <= len(path)-1:
            # print "path[i]: "
            # print path[i]
            if len(path[i]) == 0:
                pass
            elif ap in path[i]:
                states.add(i)   # because stat no from1
            i += 1
        return states

    #root: The root state's id of property.
    #Checking recursively
    # def __rverify(self, root, path, ltl, pts):
    #     if root > len(ltl)-1:
    #         return None
    #     elif ltl[root] == '&':  #conjunction
    #         lstates = self.__rverify(root*2+1, path, ltl, pts)
    #         rstates = self.__rverify(root*2+2, path, ltl, pts)
    #         if lstates is not None and rstates is not None:
    #             return lstates & rstates
    #         elif lstates is not None and rstates is None:
    #             return lstates
    #         elif lstates is None and rstates is not None:
    #             return rstates
    #         else:
    #             return None
    #     elif ltl[root] == '|': #disjunction
    #         lstates = self.__rverify(root*2+1, path, ltl, pts)
    #         rstates = self.__rverify(root*2+2, path, ltl, pts)
    #         if lstates is not None and rstates is not None:
    #             return lstates | rstates
    #         elif lstates is not None and rstates is None:
    #             return lstates
    #         elif lstates is None and rstates is not None:
    #             return rstates
    #         else:
    #             return None
    #     elif ltl[root] == '!':
    #         lstates = self.__rverify(root*2+1,path,ltl, pts)
    #         if lstates is not None:
    #             return set(range(len(path)))-lstates
    #         else:
    #             return set(range(len(path)))
    #     elif ltl[root] == 'U':
    #         lstates = self.__rverify(root*2+1, path, ltl, pts)
    #         rstates = self.__rverify(root*2+2, path, ltl, pts)
    #         if lstates is not None and rstates is not None:
    #             return self.checkU(lstates, rstates,path)
    #         elif rstates == None:
    #             return None
    #         else:
    #             return rstates
    #     elif ltl[root] == 'X':
    #         lstates = self.__rverify(root*2+1, path, ltl, pts)
    #         return self.checkX(lstates, path)
    #     else:
    #         return self.verifyAP(root, path, ltl)


    # root: id of root index in ltl
    # path: list of ap
    # ltl: linear temporal logic formula
    # pts: probabilistic transition system
    # return: a set of the index of state that satisfied in path. NOT THE STATE'S ID!

    # make some change to ltl until part
    # from "U" to "Usteps", for example "U10"
    def __rverify(self, root, path):
        ltl = self.ltl
        if root > len(ltl)-1:
            return None
        elif ltl[root] == '&':  #conjunction
            lstates = self.__rverify(root*2+1, path)
            rstates = self.__rverify(root*2+2, path)
            if lstates is not None and rstates is not None:
                return lstates & rstates
            elif lstates is not None and rstates is None:
                return lstates
            elif lstates is None and rstates is not None:
                return rstates
            else:
                return None
        elif ltl[root] == '|': #disjunction
            lstates = self.__rverify(root*2+1, path)
            rstates = self.__rverify(root*2+2, path)
            if lstates is not None and rstates is not None:
                return lstates | rstates
            elif lstates is not None and rstates is None:
                return lstates
            elif lstates is None and rstates is not None:
                return rstates
            else:
                return None
        elif ltl[root] == '!':
            lstates = self.__rverify(root*2+1,path)
            if lstates is not None:
                return set(range(len(path)))-lstates
            else:
                return set(range(len(path)))
        elif ltl[root][0] == 'U':
            try:
                steps = int(ltl[root][1:])
            except ValueError as e:
                print "until syntax error in _rverify"
                print "to specify the steps restriction in Until check"
                print "please use the form U10. "
                raise e
            lstates = self.__rverify(root*2+1, path)
            rstates = self.__rverify(root*2+2, path)
            # print("lstates: " + str(lstates))
            # print("rstates: " + str(rstates))
            if lstates is not None and rstates is not None:
                # print "entering checkU"
                states, min_rstate = self.checkU(lstates,rstates,path)
                if min_rstate > 0 and min_rstate > steps:
                    # print "until satisfied, but steps condition unsatisfied"
                    return None
                elif min_rstate > 0 and min_rstate <= steps:
                    # print "steps condition satisfied"
                    return states
                elif min_rstate < 0:
                    pass        
            elif rstates == None:
                return None
            else:
                return rstates
        elif ltl[root] == 'X':
            lstates = self.__rverify(root*2+1, path)
            return self.checkX(lstates, path)
        elif ltl[root] == 'T':
            # the True situation
            return range(len(path))
        else:
            return self.verifyAP(root, path, ltl)

    #Get the expectation value of posterior distribution.
    def postEx(self, a, b, n, x):
        return (a+x)/(n+a+b)

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

        sz = int(s.getMaxSize(s.a, s.b, s.c, s.d))
        # event = self.FinishEventClass(output='The upper bound of sample size is '+str(sz))
        # wx.PostEvent(self.frame, event)

        # event = self.FinishEventClass(output='Verifying...')
        # wx.PostEvent(self.frame, event)

        x,n = 0.0, 0.0
        postex = 0.0
        for i in range(sz):
            path, satisfied = s.getPath(self.decided_prefixes)
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
        s = self
        sz = s.getMaxSize(s.a, s.b, s.c, s.d)
        x,n = 0.0,0.0
        for i in range(sz):
            path, satisfied = s.getPath()
            n += 1
            if s.verify([p.ap for p in path], s.ltl, s.k):
                x += 1
        postex = s.postEx(s.a, s.b, n, x)
        l = postex-s.d
        h = postex+s.d
        l = 0 if l<0 else l
        h = 1 if h>1 else h

        # event = self.FinishEventClass(output=str(int(n))+' samples are verified.')
        # wx.PostEvent(self.frame, event)

        return l,h

    #Begin to check.
    def run(self):
        msg = None
        if self.type == 0:
            self.is_satisfy = self.mc1()
            if self.is_satisfy:
                msg = "The model satisfies the LTL."
            else:
                msg = "The model does not satisfy the LTL."
        else:
            self.lower,self.upper =  self.mc2()
            msg = "The probability is ["+str(self.lower)+","+str(self.upper)+"]."

        #Post the event
        # event = self.FinishEventClass(output=msg)
        # wx.PostEvent(self.frame, event)


def get_die_model():
    # build the pts
    s1post = [[2,0.5], [3,0.5]]
    s1ap=set()
    s1 = state(1, s1post, s1ap)

    s2post=[[4,0.5], [5,0.5]]
    s2ap=set()
    s2=state(2, s2post, s2ap)

    s3post = [[6,0.5], [7, 0.5]]
    s3ap=set()
    s3 = state(3, s3post, s3ap)

    s4post = [[8,0.5], [2,0.5]]
    s4ap=set()
    s4 = state(4, s4post, s4ap)

    s5post=[[9,0.5], [10,0.5]]
    s5ap = set()
    s5 = state(5, s5post, s5ap)

    s6post=[[11,0.5], [12,0.5]]
    s6ap= set()
    s6 = state(6, s6post, s6ap)

    s7post = [[13,0.5], [3,0.5]]
    s7ap=set()
    s7 = state(7, s7post, s7ap)

    s8post = [[8,1]]
    s8ap=set()
    s8ap.add("1")
    s8=state(8, s8post, s8ap)

    s9post=[[9,1]]
    s9ap=set()
    s9ap.add("2")
    s9=state(9,s9post, s9ap)

    s10post=[[10,1]]
    s10ap=set()
    s10ap.add("3")
    s10 = state(10, s10post , s10ap)

    s11post=[[11,1]]
    s11ap=set(["4"])
    s11=state(11, s11post, s11ap)

    s12post=[[12,1]]
    s12ap=set(["5"])
    s12= state(12, s12post , s12ap)

    s13post = [[13,1]]
    s13ap = set(["6"])
    s13= state(13, s13post, s13ap)

    return [13, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]

#Only 1 test case
def test():
    next='X'
    until='U'
    neg='!'
    dis='|'
    con='&'

    a=1.0
    b=1.0
    c=0.99
    d=0.02
    k=10
    p=0.02
    op='>'
    
    pts = get_die_model()
    ltl = ["U3", "T", "2"]
    #  print "ltl:"
    print "ltl:"
    print ltl
    ck=Checker(pts, ltl, a, b, c, d, k, p, op,1,None)
    result=ck.mc1()
    print(result)

if __name__=='__main__':
    # pass
  test()




# app = wx.PySimpleApp()
# app.TopWindow = Test()
# app.TopWindow.Show()
# app.MainLoop()


