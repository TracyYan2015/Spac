#!/usr/bin/python
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.ModulesFile as ModulesFile
import logging
logging.basicConfig(level=logging.DEBUG)

allUpCnt = 0
failureCnt = 0

class ModulesFileTest(unittest.TestCase):
    # def testCreationModulesFile(self):
    #     modulesFile = ModulesFile.GYNCTMCModel()
    #     self.assertTrue(len(modulesFile.modules) == 5)

    # def testLabel(self):
    #     modulesFile = ModulesFile.GYNCTMCModel()
    #     initState = modulesFile.genState()
    #     self.assertTrue(initState.checkAP('up'))
    #     self.assertFalse(initState.checkAP('down'))
    #     self.assertFalse(initState.checkAP('danger'))
    DURATION = float(3600 * 24 * 365)  # one year

    def testGenRandomPath2(self):
        # model = ModulesFile.GYNCTMCModel()
        # result,path = model.genRandomPath(self.DURATION, cachedPrefixes=dict())
        # model.exportPathTo(path, 'path1.txt')
        pass

    def testFailureBiasing(self):
        model = ModulesFile.BalancedModel()
        delta = 0.8
        model.SFB(delta)
        def allUpOrFailure(vs, cs):
            i = vs['i']
            di = vs['di']
            a = vs['a']
            global allUpCnt
            global failureCnt
            # all components up
            if i == 1 and di == 1 and a == 1:
                allUpCnt += 1
                return True
            # one kinds of component all failure
            if i == 0 and di == 0:
                failureCnt += 1
                return True
            if a == 0:
                failureCnt += 1
                return True
            return False
        for i in range(10000):
            result, path = model.genRandomPath(self.DURATION, cachedPrefixes=dict(), stopCondition=allUpOrFailure)
        logging.info("allUpCnt = %d, failureCnt = %d\n" % (allUpCnt, failureCnt))

    def testFailureStates(self):
        model = ModulesFile.BalancedModel()
        failurestates = model._failuredstates()
        logging.info(str(failurestates))


    def testGenRandomPath(self):
        model = ModulesFile.BalancedModel()
        model.forcing = True
        delta = 0.5
        model.BFB(delta)
        duration = 5*365*24*3600
        for i in range(3):
            path = model.genRandomPath(duration)
            logging.info(str(path))


if __name__ == '__main__':
    unittest.main()
