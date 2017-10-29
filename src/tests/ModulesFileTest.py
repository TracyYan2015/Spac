#!/usr/bin/python
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.ModulesFile as ModulesFile
import pickle

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

    def testGenRandomPath2(self):
        model = ModulesFile.GYNCTMCModel()
        duration = float(3600)
        result,path = model.genRandomPath(duration)
        model.exportPathTo(path, 'path.txt')


if __name__ == '__main__':
    unittest.main()
