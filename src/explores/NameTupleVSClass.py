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
        NTState = collections.namedtuple('State', 'stateId postStates apSet')
        s1 = NTState(1, [None, None], set('abc'))
        class State:
            def __init__(self, stateId, postStates, apSet):
                self.stateId = stateId
                self.postStates = postStates
                self.apSet = apSet

        s1Class = State(1, [None, None], set('abc'))
        logging.info('namedtuple instance size: %s' % str(sys.getsizeof(s1)))
        logging.info('class instance size: %s' % str(sys.getsizeof(s1Class)))        
        self.assertTrue(sys.getsizeof(s1) < sys.getsizeof(s1Class))

if __name__ == '__main__':
    unittest.main()