#!/usr/bin/python
# -*- coding=utf-8 -*-
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import logging
logging.basicConfig(level=logging.DEBUG, filename = 'PrepCommTest.log', filemode='w')
import explores.Module as Module
import explores.ModulesFile as ModulesFile
import itertools

class PrepCommTest(unittest.TestCase):
    def test(self):
        model = ModulesFile.GYNCTMCModel()
        model.prepareCommands()
        for vStr, comms in model.scDict.items():
            logging.info(vStr)
            logging.info(str([comm.name for comm in comms]))

if __name__ == '__main__':
    unittest.main()