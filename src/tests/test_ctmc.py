#!/usr/bin/python
import unittest
import os, sys
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir)+os.path.sep+".")
sys.path.append(parDir)
import CheckerCTMC
import models.Models as Models
import logging
import ModulesFile

class CTMCTestCase(unittest.TestCase):
    def testGetRandomPath(self):
        ctmc = Models.TestCTMCModel # [#states, [state]]
        duration = 3
        checker = CheckerCTMC.CheckerCTMC(ctmc=ctmc, duration=duration)
        path = checker.getRandomPath(duration)
        duration2 = reduce(lambda x,y: x+y, [t[1] for t in path])
        self.assertAlmostEqual(duration, duration2,delta=1e-6)

    def testUntilCheck(self):
        ctmc = Models.TestCTMCModel # [#states, [state]]
        ltl = ['U[0,10]', 'default', 'full']
        checker = CheckerCTMC.CheckerCTMC(ctmc=ctmc, csl=ltl, duration=3)
        for _ in range(200):
            path = checker.getRandomPath()
            stateIds = set([stateTuple[0].stateId for stateTuple in path])
            # logging.info("CHECKING UNTIL")
            # logging.info("path: " + str([str(stateTuple[0]) for stateTuple in path]))
            result = checker.verify(path, ltl)
            # logging.info("checking result: %s" % str(result))
            self.assertEqual((3 in stateIds), result)

    def testUntilCheckGYNModel(self):
        model = ModulesFile.GYNCTMCModel()
        # ltl: true U<=315360000 "down" # 10 years!
        ltl = ['U[0, 315360000]', 'T', 'down']
        # duration1 = float(0.001*365*24*3600)
        checker = CheckerCTMC.CheckerCTMC(csl=ltl, duration=315360000)



if __name__ == '__main__':
    unittest.main()
