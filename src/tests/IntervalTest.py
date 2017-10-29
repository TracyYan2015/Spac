#!/usr/bin/python
# -*- coding=utf-8 -*-
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import logging 
logging.basicConfig(level=logging.DEBUG, filename = 'ModuleTest.log', filemode='w')
import Checker


class IntervalTest(unittest.TestCase):
    def testInterleave(self):
        interval1 = Checker.Interval(0,10)
        interval2 = Checker.Interval(4,11)
        interval3 = Checker.Interval(0,10)
        interval4 = Checker.Interval(12,14)
        interval5 = Checker.Interval(4, -1)
        interval6 = Checker.Interval(2,3)
        interval7 = Checker.Interval(3,-1)
        interval8 = Checker.Interval(1,-1)
        self.assertTrue(interval1.interleaveWith(interval2))
        self.assertTrue(not interval3.interleaveWith(interval4))
        self.assertTrue(not interval5.interleaveWith(interval6))
        self.assertTrue(interval7.interleaveWith(interval8))



if __name__ == '__main__':
    unittest.main()