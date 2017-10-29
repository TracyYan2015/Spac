#!/usr/bin/python
import time, copy

class State:
    def __init__(self, apSet=None, _id=None):
        self.id = _id
        self.apSet = apSet

    # def __init__(self, another):
    #     if another:
    #         self.id = another.id
    #         self.apSet = another.apSet


s = State(None)
s.id = 0
s.apSet = set(['abc'])
b = time.time()
for i in range(3600):
    # s1 = copy.copy(s)
    s1 = State(s.apSet, s.id)
e = time.time()
print 'time: %ss' % str(e-b)

# b = time.time()
# for i in range(3600):
#     # s1 = copy.copy(s)
#     s1 = State(s)
# e = time.time()
# print 'time: %ss' % str(e-b)