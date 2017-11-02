#!/usr/bin/python
# -*- coding:utf-8 -*-
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.Step as Step
import collections
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

# From fluent python:
# Test whether
# collections.namedtuple consumes less memory compared to normal class
# SEEMS NOT RIGHT!!!!!
class Test(unittest.TestCase):
    def testNamedTupleVSClass(self):
        step = Step.Step(10, set('afaoijfija'), 9.0, 9.0)
        path1 = [step for i in range(200000)]
        TupleStep = collections.namedtuple('step', ['stateId', 'apSet', 'passedTime', 'holdingTime'])
        tStep = TupleStep(10, set('afaoijfija'), 9.0, 9.0)
        path2 = [tStep for i in range(200000)]
        logging.info('instance length: %dB' % sys.getsizeof(step))
        logging.info('named tuple length: %dB' % sys.getsizeof(tStep))

if __name__ == '__main__':
    unittest.main()