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
import explores.PRISMState as PRISMState
import explores.ModulesFile as ModulesFile
import time
import CheckerCTMC

class TestCTMCChecker(unittest.TestCase):
    def testCheckerUntil(self):
        # compute the probability of satisfy a until formula
        YEAR = float(31536000)
        MONTH = float(31*24*3600)
        model = ModulesFile.GYNCTMCModel()
        csl = ['U[0,2678400]', 'T', 'down']
        checker = CheckerCTMC.CheckerCTMC(modulesFile = model, csl=csl, duration=MONTH, checkingType=1)
        begin = time.time()
        lowerBound, upperBound = checker.run()
        end = time.time()
        logging.info('Time caused to check the prob satisfying %s: %ss' % (str(end-start), str(csl)))
        logging.info('lowBound = %s, highBound = %s' % (str(lowerBound), str(upperBound)))



if __name__ == '__main__':
    unittest.main()