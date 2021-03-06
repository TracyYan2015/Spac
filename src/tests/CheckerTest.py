#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, filename='ModulesFileGenPath.log', filemode='w')
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.ModulesFile as ModulesFile
import time
from Checker import Checker

class CheckerTest(unittest.TestCase):
    def testCheckerUntil(self):
        # compute the probability of satisfy a until formula
        YEAR = float(31536000)
        MONTH = float(31*24*3600)
        HOUR = float(3600)
        model = ModulesFile.GYNCTMCModel()
        ltl = ['U[0,600]', 'T', 'down']
        checker = Checker(model = model, ltl=ltl, duration=HOUR/6, checkingType=Checker.CheckingType.QUANTATIVE)
        begin = time.time()
        lowerBound, upperBound = checker.run()
        end = time.time()
        logging.info('Time caused to check the prob satisfying is %ss: %ss' % (str(end-begin), str(ltl)))
        logging.info('lowBound = %s, highBound = %s' % (str(lowerBound), str(upperBound)))



if __name__ == '__main__':
    unittest.main()