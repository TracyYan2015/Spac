#!/usr/bin/python
# -*- coding:utf-8 -*-
import unittest
import collections
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

# From fluent python:
# Test whether
# collections.namedtuple consumes less memory compared to normal class
# SEEMS NOT RIGHT!!!!!
class Test(unittest.TestCase):
    def testNamedTupleVSClass(self):
        

if __name__ == '__main__':
    unittest.main()