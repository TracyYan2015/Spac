#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import time
import explores.Step as Step
import Checker


class DecidedPrefixTest(unittest.TestCase):
    def test1(self):
        # ltl: [Xa & (b U[0,10] c)]
        # path: [b, ab, b, c]
        path = []
        step1 = Step.Step(0, set('b'), 0,0)
        step2 = Step.Step(1, set('ab'), 0,0)
        step3 = Step.Step(2, set('b'), 0,0)
        step4 = Step.Step(4, set('c'), 0, 0)
        path.append(step1)
        path.append(step2)
        path.append(step3)
        path.append(step4)
    
    
        checker = Checker.Checker()
        checker.ltl = ['&', 'X', 'U[0,10]', 'a', '', 'b', 'c']
        prefix = checker._get_decidable_prefix(path, path[0], 0)
        logging.info('ltl: [Xa & (b U[0,10] c)]')
        logging.info('path: %s' % str([step.apSet for step in path]))
        logging.info('prefix:')
        for step in prefix:
            logging.info(str(step))
        self.assertTrue(len(prefix) == 4)

    def test2(self):
        # ltl: [Xa & (b U[0,10] c)]
        # path: [b, ab, a, c]
        path = []
        step1 = Step.Step(0, set('b'), 0,0)
        step2 = Step.Step(1, set('ab'), 0,0)
        step3 = Step.Step(2, set('a'), 0,0)
        step4 = Step.Step(4, set('c'), 0, 0)
        path.append(step1)
        path.append(step2)
        path.append(step3)
        path.append(step4)
        checker = Checker.Checker()
        checker.ltl = ['&', 'X', 'U[0,10]', 'a', '', 'b', 'c']
        prefix = checker._get_decidable_prefix(path, path[0], 0)
        logging.info('ltl: [Xa & (b U[0,10] c)]')
        logging.info('path: %s' % str([step.apSet for step in path]))
        logging.info('prefix:')
        for step in prefix:
            logging.info(str(step))
        self.assertTrue(len(prefix) == 3)

    def test3(self):
        # ltl: [Xa & (b U[0,10] c)]
        # path: [b, ab, ab, ab]
        path = []
        step1 = Step.Step(0, set('b'), 0,0)
        step2 = Step.Step(1, set('ab'), 0,0)
        step3 = Step.Step(2, set('ab'), 0,0)
        step4 = Step.Step(4, set('ab'), 0, 0)
        path.append(step1)
        path.append(step2)
        path.append(step3)
        path.append(step4)
        checker = Checker.Checker()
        checker.ltl = ['&', 'X', 'U[0,10]', 'a', '', 'b', 'c']
        prefix = checker._get_decidable_prefix(path, path[0], 0)
        logging.info('ltl: [Xa & (b U[0,10] c)]')
        logging.info('path: %s' % str([step.apSet for step in path]))
        logging.info('prefix:')
        for step in prefix:
            logging.info(str(step))
        self.assertTrue(len(prefix) == 4)


if __name__ == '__main__':
    unittest.main()