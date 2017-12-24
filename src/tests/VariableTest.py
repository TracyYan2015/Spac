#!/usr/bin/python

# unittest for Variable class to represent variable in PRISM,
# which can only be boolean or integer(bounded or unbounded)
import unittest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys, os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir) + os.path.sep + '.')
# logging.info('curDir: %s' % str(curDir))
# logging.info('parDir: %s' % str(parDir))
sys.path.append(parDir)

import explores.Module as Module

class VariableTest(unittest.TestCase):
    def test(self):
        # create Variable instance of type bounded integer
        v = Module.Variable('', 0, range(3), int, True)
        self.assertTrue(v.validate(1))
        self.assertFalse(v.validate(4))
        
        # unbounded integer
        v = Module.Variable('', 0, None, int, False)
        self.assertTrue(v.validate(10))

        # boolean
        v = Module.Variable('', True, set([True, False]), bool, True)
        self.assertTrue(v.validate(True))
        self.assertFalse(v.validate(10))

        # equal test
        v = Module.Variable('', 0, range(3), int, True)
        self.assertTrue(v == 0)
        self.assertFalse(v == 1)

        # in-place add test
        v += 1
        self.assertTrue(v == 1)


if __name__ == '__main__':
    unittest.main()
