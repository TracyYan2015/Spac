#!/usr/bin/python
# -*- coding=utf-8 -*-
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.Module as Module
import logging 
logging.basicConfig(level=logging.DEBUG, filename = 'ModuleTest.log', filemode='w')
import explores.Module as Module

class ModuleTest(unittest.TestCase):
    def testCTMCModule(self):
        AT697F = Module.AT697F
        # test guard
        self.assertFalse(AT697F.commands[0].guard())
        AT697F.d.value = 2
        self.assertTrue(AT697F.commands[0].guard())
        # test action
        AT697F.commands[0].action()
        self.assertTrue(AT697F.d.value == 0)
        # test constants
        self.assertTrue(AT697F.constants['fail_d'] == 1.0/(10*365*24*3600))

    def testVariable(self):
        var1 = Module.Variable('d', 0, range(3), int, True)
        var2 = Module.Variable('d', 1, range(3), int, True)
        self.assertTrue(var1 < 2)
        self.assertTrue(var1 < var2)


if __name__ == '__main__':
    unittest.main()