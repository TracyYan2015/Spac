# import numpy as np
# import scipy.stats as stats
import random
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='spac.log',
                filemode='w')

class State():
    def __init__(self, _id, postStates, ap):
        #need to be checked
        self.id = _id
        # preStates = preStates
        self.postStates = postStates
        self.ap = ap

    def __str__(self):
        return str(self.id) + ":" + str(self.ap)


def APOf(state_list):
    return list(map(lambda x: x.ap, state_list))

no = list()
# s1pre = no
s1post = [[2,0.4], [3,0.6]]
s1ap=set()
s1ap.add('c')
s1=State(1,s1post,s1ap)

s2post = no
s2ap=set()
s2ap.add('a')
s2=State(2,s2post,s2ap)

s3post = no
s3ap=set()
s3ap.add('a')
s3ap.add('b')
s3ap.add('c')
s3=State(3,s3post,s3ap)

pts = [3, s1, s2, s3]

next='X'
con='&'
dis='|'
neg='!'
until='U'

ltl1 = [con, until, next, next, 'b', 'c', None, 'a']
ltl2 = [until, next, 'b', 'a']
ltl3 = [next, 'a']
ltl4 = ['b']
ltl5 = [next, 'c']
# path = [set('c'), set(['a','b','c'])]
path = [s1,s3]


def modelCheckTest():
    path = [s1, s3]
    # print verify(path, ltl1) # True
    print getKeyState(path, ltl1, 0)

# tree: a binary complete tree
# root: the root of the wanted subtree
# return: the subtree in a list form
def getSubTree(tree, root):
    result = list()
    result.append(tree[root])
    return None

global key_states
key_states = list()


# get maximum state in terms of state's id
def max_state_of(states):
    # print states
    if states is None or len(states) == 0:
        return None
    return max(states, key=lambda x: x.id)

# get minimum state in terms of state's id 
def min_state_of(states):
    if states is None or len(states) == 0:
        return None
    return min(states, key=lambda x: x.id)


def get_decidable_prefix_test():
    path = [s1, s2]
    ltl = [dis, 'c', next, None, None, 'a']
    prefix = get_decidable_prefix(path, 0, ltl, 0)
    print "prefix:"
    for p in prefix:
        print p

def rverify_until_test():
    pts = get_die_model()
    path = get_random_path(pts, 10, None)
    print("path:")
    for p in path:
        print p
    ltl = ["U3", "T", "2"]
    res = _rverify(0, [p.ap for p in path], ltl, None)
    print "_rverify result: " + str(res)



def get_key_state_until_test():
    path = [s1, s3]
    ltl = [until, next, 'b', 'a']
    print get_key_state(path, 0, ltl, 0).id  # 3

# get random path with decided_prefixes
# pts: the model
# k: the path length
# return: list of states
def get_random_path(pts, k, decided_prefixes):
    import copy
    path = list()
    sid = 1 #stateid
    # insert copy of state's object into path
    # to make all elements in path with same state_id have distinct ids(in python)
    path.append(copy.copy(pts[sid]))

    for i in range(k):
        rnd = random.random() # x in interval [0,1)
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

    return path

# return the pts of the die(shaizi) model
def get_die_model():
    # build the pts
    s1post = [[2,0.5], [3,0.5]]
    s1ap=set()
    s1 = State(1, s1post, s1ap)

    s2post=[[4,0.5], [5,0.5]]
    s2ap=set()
    s2=State(2, s2post, s2ap)

    s3post = [[6,0.5], [7, 0.5]]
    s3ap=set()
    s3 = State(3, s3post, s3ap)

    s4post = [[8,0.5], [2,0.5]]
    s4ap=set()
    s4 = State(4, s4post, s4ap)

    s5post=[[9,0.5], [10,0.5]]
    s5ap = set()
    s5 = State(5, s5post, s5ap)

    s6post=[[11,0.5], [12,0.5]]
    s6ap= set()
    s6 = State(6, s6post, s6ap)

    s7post = [[13,0.5], [3,0.5]]
    s7ap=set()
    s7 = State(7, s7post, s7ap)

    s8post = [[8,1]]
    s8ap=set()
    s8ap.add("1")
    s8=State(8, s8post, s8ap)

    s9post=[[9,1]]
    s9ap=set()
    s9ap.add("2")
    s9=State(9,s9post, s9ap)

    s10post=[[10,1]]
    s10ap=set()
    s10ap.add("3")
    s10 = State(10, s10post , s10ap)

    s11post=[[11,1]]
    s11ap=set(["4"])
    s11=State(11, s11post, s11ap)

    s12post=[[12,1]]
    s12ap=set(["5"])
    s12= State(12, s12post , s12ap)

    s13post = [[13,1]]
    s13ap = set(["6"])
    s13= State(13, s13post, s13ap)

    return [13, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]


def die_decide_prefix_test():
    pts = get_die_model()
    decided_prefixes = {}
    path = get_random_path(pts, 10, decided_prefixes)
    print "random path:"
    for p in path:
        print p
    print "ltl:"
    ltl = ['U3', 'T', '|', None, None, '2', '3']
    print ltl
    satisfied = verify([s.ap for s in path], ltl, 0)
    print "satisfied result:"
    print str(satisfied)
    try:
        prefix = get_decidable_prefix(path, 0, ltl, 0)
    except Exception as e:
        print e.message
        raise e
    if satisfied:
        decided_prefixes[str(prefix)] = True
    else:
        decided_prefixes[str(prefix)] = False
    print "prefix: "
    for prefix_state in prefix:
        print prefix_state



# variables same with get_key_state
def get_decidable_prefix(path, state_id, ltl, ltl_root):
    print "result of get_key_state: "
    key_state = get_key_state(path, state_id, ltl, ltl_root)
    print key_state
    # using the id of keystate object to get the prefix
    idx = [id(p) for p in path].index(id(key_state))
    return path[0:idx+1]



# movedtochecker.py
# path: list of states
# state_id: the index of state in path, NOT the state'id
# return: the key state object
def get_key_state(path, state_id, ltl, ltl_root):
    ltl_root_symbol = ltl[ltl_root]
    if ltl_root_symbol == '&':
        res_states = _rverify(ltl_root, [p.ap for p in path], ltl, None)
        if state_id in res_states:
            # path[state_id] satisfies y1&y2
            return max_state_of([get_key_state(path, state_id, ltl, ltl_root*2+1), get_key_state(path, state_id, ltl, ltl_root*2+2)])
        else:
            # compute the states that satisfy y1
            res_left_states = _rverify(ltl_root*2+1, [p.ap for p in path], ltl, None)
            # compute the states that satisfy y2
            res_right_states = _rverify(ltl_root*2+2, [p.ap for p in path], ltl, None)
            
            # y1 satisfied and y2 not satisfied
            if state_id in res_left_states and state_id not in res_right_states:
                return get_key_state(path, state_id, ltl, ltl_root*2+2)
            elif state_id not in res_left_states and state_id in res_right_states:
                return get_key_state(path, state_id, ltl, ltl_root*2+1)
            else:
                return min_state_of([get_key_state(path, state_id, ltl, ltl_root*2+1), get_key_state(path, state_id, ltl, ltl_root*2+2)])
    elif ltl_root_symbol == '|':
        res_states = _rverify(ltl_root, [p.ap for p in path], ltl, None)
        if state_id in res_states:
            # path[state_id] satisfied y1|y2
            # compute the states that satisfy y1
            res_left_states = _rverify(ltl_root*2+1, [p.ap for p in path], ltl, None)
            # compute the states that satisfy y2
            res_right_states = _rverify(ltl_root*2+2, [p.ap for p in path], ltl, None)
            if state_id in res_left_states and state_id not in res_right_states:
                return get_key_state(path, state_id, ltl, ltl_root*2+1)
            elif state_id not in res_left_states and state_id in res_right_states:
                return get_key_state(path, state_id, ltl, ltl_root*2+2)
            else:
                return min_state_of([get_key_state(path, state_id, ltl, ltl_root*2+1), get_key_state(path, state_id, ltl, ltl_root*2+2)])
        else:
            # y1|y2 not satisfied
            return max_state_of([get_key_state(path, state_id, ltl, ltl_root*2+1), get_key_state(path, state_id, ltl, ltl_root*2+2)])
    elif ltl_root_symbol == 'X':
        return get_key_state(path, state_id+1, ltl, ltl_root+1)
    elif ltl_root_symbol == '!':
        # return get_key_state(path, state_id+1, ltl, ltl_root+1)
        return get_key_state(path, state_id, ltl, ltl_root+1)
    # add steps restriction to until check
    # change 'U' to "Usteps" e.g. "U10"
    elif ltl_root_symbol[0] == 'U':
        if len(ltl_root_symbol) > 0:
            try:
                steps = int(ltl_root_symbol[1:])
            except Exception as e:
                print "until syntas invalid, use 'Usteps' "
        res_states = _rverify(ltl_root, [p.ap for p in path], ltl, None)
        if state_id in res_states:
            # y1Uy2 satisfied
            res_right = _rverify(ltl_root*2+2, [p.ap for p in path], ltl, None)
            # print "states that satisfy y2"
            # print res_right
            # get the minimum id of state that satisfies y2(the right formula)
            # list of states that satisfied y2
            right_min_id = min(res_right)
            # print right_min_id
            test_ids = range(right_min_id)
            # print test_ids
            state_y1 = max_state_of([get_key_state(path, state_id, ltl, ltl_root*2+1) for state_id in test_ids])
            state_y2 = get_key_state(path, right_min_id, ltl, ltl_root*2+2)
            # state_y2 = max_state_of([get_key_state(path, state_id, ltl, ltl_root*2+2) for state_id in test_ids])
            return max_state_of([state_y1, state_y2])
        else:   
            # y1Uy2 not satisfied
            res_left_states = _rverify(ltl_root*2+1, [p.ap for p in path], ltl, None)
            res_right_states = _rverify(ltl_root*2+2, [p.ap for p in path], ltl, None)
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
            tmp1 = max_state_of([get_key_state(path, state_id, ltl, ltl_root*2+2) for state_id in test_ids])
            return max_state_of([get_key_state(path, state_id-1, ltl, ltl_root*2+1), get_key_state(path, state_id-1, ltl, ltl_root*2+2), tmp1])
    else:
        # ltl is AP
        if state_id >= len(path) or state_id < 0:
            print "IndexError: " + str(state_id)
        return path[state_id]


# return whether ap_path satisfy the ltl
def verify(ap_path, ltl, root):
    result = _rverify(root, ap_path, ltl, None)
    if result is not None:
        return root in result
    else:
        return False

# movedtochecker.py
# root: id of root index in ltl
# path: list of ap
# ltl: linear temporal logic formula
# pts: probabilistic transition system
# return: a set of the index of state that satisfied in path. NOT THE STATE'S ID!

# make some change to ltl until part
# from "U" to "Usteps", for example "U10"
def _rverify(root, apPath, ltl, pts=None):
    if root > len(ltl)-1:
        return None
    elif ltl[root] == '&':  #conjunction
        lstates = _rverify(root*2+1, apPath, ltl, pts)
        rstates = _rverify(root*2+2, apPath, ltl, pts)
        logging.info("lstates: "+str(lstates))
        logging.info("rstates: "+str(rstates))
        return lstates & rstates
    elif ltl[root] == '|': #disjunction
        lstates = _rverify(root*2+1, apPath, ltl, pts)
        rstates = _rverify(root*2+2, apPath, ltl, pts)
        return lstates | rstates
    elif ltl[root] == '!':
        lstates = _rverify(root*2+1,apPath,ltl, pts)
        if lstates is not None:
            return set(range(len(apPath)))-lstates
        else:
            return set(range(len(apPath)))
    elif ltl[root][0] == 'U':
        if len(ltl[root]) > 0:
            try:
                steps = int(ltl[root][1:])
            except ValueError as e:
                print "until syntax error in _rverify"
                # raise e
        lstates = _rverify(root*2+1, apPath, ltl, pts)
        rstates = _rverify(root*2+2, apPath, ltl, pts)
        print("lstates: " + str(lstates))
        print("rstates: " + str(rstates))
        if lstates is not None and rstates is not None:
            # print "entering checkU"
            states, min_rstate = checkU(lstates, rstates,apPath)
            if min_rstate > steps:
                print "until satisfied, but steps condition unsatisfied"
                return None
            else:
                print "steps condition satisfied"
                return states
        elif rstates == None:
            return None
        else:
            return rstates
    elif ltl[root] == 'X':
        lstates = _rverify(root*2+1, apPath, ltl, pts)
        return checkX(lstates, apPath)
    elif ltl[root] == 'T':
        # the True situation
        return range(len(apPath))
    else:
        return verifyAP(root, apPath, ltl)

# movedtochecker.py
# lstates, rstates: set of states that satisfy y1 and y2
def checkU(lstates, rstates, apPath):
    if rstates == None:
        return None
    
    i = len(apPath)-1
    states = set()
    started = False
    # the idea here...
    # if there's state i that satisfy y2
    # and any states that before i satisfy y1
    # then add both i and j(<i) to states.

    # min_rstate: the minimum index of state in path that satisfy y2
    min_rstate = max(rstates)
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

# movedtochecker.py
def checkX(lstates, apPath=None):
    if lstates==None:
        return None
    states = set()
    for sid in lstates:
        if(sid-1 >= 0):
            states.add(sid-1)
    return states

# root: current symbol under checked in ltl
# apPath: list of 
def verifyAP(root, apPath, ltl):
    if(root > len(ltl)-1):
        return set()
    ap = ltl[root]
    i = 0  #order in apPath
    states = set()
    for i,stateAP in enumerate(apPath):
        if ap in stateAP:
            states.add(i)
    return states

# a and b: parameters of beta distribution
# n: # of current tested cases
# x: # of successful current tested cases
# n0: total cases to be sampled
# d: accuracy parameter
# q: the probability parameter
def predictQualitativeStatistics(a, b, n, x, n0, d,q):
    exmin=expt(a,b,x,n0)
    exmax=expt(a,b,x+n0-n,n0)
    # print("min expectation: " + str(exmin) + " max expectation: " + str(exmax))
    # if q is in [exmin-d, exmin+d] and q is in [exmax-d, exmax+d]
    # then return true
    # else return false
    if (q>=(exmin-d) and q<= (exmin+d)) or (q>=(exmax-d) and q<=(exmax+d)):
        # print("True")
        return True
    else:
        # print("False")
        return False

def predictQuantativeStatistics(a,b,n,x,n0,d):
    # current posterior expectation
    ex2=expt(a,b,x,n)
    exmin=expt(a,b,x,n0)
    exmax=expt(a,b,x+n0-n,n0)
    print("min expectation: " + str(exmin) + " max expectation: " + str(exmax))
    if (exmax-ex2) < d and (ex2-exmin) < d:
        return True
    else:
        return False

# return the string concated with all the aps in path
def str_of(path):
    return str(path)


def predTest():
    a=1.0
    b=1.0
    c=map(lambda x: float(x)/100, range(50, 95, 5))
    d=map(lambda x: float(x)/100, range(1, 30))
    r=map(lambda x: float(x)/10, range(1,10))
    print("c\td\tr\tsize\ttest_rate")
    for _c in c:
        for _d in d:
            for _r in r:
                size = getSampleSize(a,b,_c,_d)
                # print("c\td\tr\tsize\ttest_rate")
                n = 0
                succ = 0
                # print("r: " + str(_r))
                for x in stats.binom.rvs(n=1, p=_r, size = size):
                    if x > 0:
                        succ += 1
                    n += 1
                    if predictQualitativeStatistics(a,b,n,succ,size,_d,_r):
                        # print(str(float(n)/size)+" cases tested")
                        print(str(_c)+'\t' + str(_d)+'\t'+str(_r)+'\t'+str(size) + '\t' + str(float(n)/size))
                        break

# return the expectation of posterior beta distribution.
def expt(a,b,x,n0):
    return (a+x)/(a+b+n0)

def getSampleSize(a,b,c,d):
    return int(1.0/((1-c)*4*d*d)-a-b-1)


def main():
    # pass
    # modelCheckTest()
    # predTest()
    # get_decidable_prefix_test()
    die_decide_prefix_test()
    # get_key_state_until_test()
    # a=1.0
    # b=1.0
    # c_list = map(lambda x:float(x)/100, range(100))
    # d=0.02
    # # the actual probability that the model satisfy some property
    # r = 0.78
    # for c in c_list:
    #   size = getSampleSize(a,b,c,d)
    #   print("sample size:" + str(size))
    #   print("c: " + str(c))
    #   succ = 0
    #   n = 0
    #   q = 0.78
    #   # generate 0-1 distribution array
    #   for x in stats.binom.rvs(n=1, p=r, size = size):
    #       if x > 0:
    #           succ += 1
    #       n += 1
    #       if predictQualitativeStatistics(a, b, n, succ, size, d, q):
    #           # print("c: " + str(c))
    #           print(str(float(n)/size) + " tested")
    #           break

if __name__ == "__main__":
    main()
