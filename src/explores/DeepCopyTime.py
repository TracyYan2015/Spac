#!/usr/bin/python
from ModulesFile import GYNCTMCModel
import time, copy

model = GYNCTMCModel()
state = model.getCurrentState()
begin = time.time()
for i in range(1):
    copy.deepcopy(range(360000))
end = time.time()
print 'deeptime: ' + str(end - begin)
begin = time.time()
for i in range(1):
    copy.copy(range(360000))
end = time.time()
print 'time: ' + str(end - begin)
