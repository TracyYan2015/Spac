#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG, filename="TestUtils.log", filemode='w')
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import utils.MathUtils as MathUtils


class TestUtils(unittest.TestCase):
    def testRandomExpo(self):
        lamda = 1.0/(5*365*24*3600)
        t = 5*365*24*3600
        for i in range(1000000):
            rnd = MathUtils.randomExpo(lamda, t)
            logging.info(rnd)
            self.assertTrue(rnd <= t and rnd >= 0)
