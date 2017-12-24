#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
from explores import ModulesFile


class FailureBiasingTest(unittest.TestCase):
    def testSimpleBiasing(self):
        model = ModulesFile.BalancedModel()
        delta = 0.5
        model.SFB(delta)
        logging.info("finished")

    def testBalancedBiasing(self):
        model = ModulesFile.BalancedModel()
        delta = 0.5
        model.BFB(delta)
        logging.info("finished")
        

