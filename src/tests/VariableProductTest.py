#!/usr/bin/python
# -*- coding=utf-8 -*-
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import logging
logging.basicConfig(level=logging.DEBUG, filename = 'VarProdTest.log', filemode='w')
import explores.Module as Module
import explores.ModulesFile as ModulesFile
import itertools

class VarProdTest(unittest.TestCase):
    def test(self):
        model = ModulesFile.GYNCTMCModel()
        i = 0
        for vList in itertools.product(*[v.allVarsList() for _,v in model.localVars.items()]):
            if i <= 1000:
                i += 1
                for v in vList:
                    logging.info(v.name + ': ' + str(v.value))

if __name__ == '__main__':
    unittest.main()