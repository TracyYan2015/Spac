#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, filename='ModulesFileGenPath.log', filemode='w')
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import time
from collections import OrderedDict

class CallVSDictUpdate(unittest.TestCase):
    def doSomething(self):
        pass

    # compare the time consumed when calling a function and update a dict
    # it seems function call is quicker than dict update
    # it seems that create new object in python is quite time-consuming.
    def test(self):
        b = time.time()
        for i in range(3600000):
            self.doSomething()
        e = time.time()
        logging.info('function calling: %ds' % (e-b))
        
        d1 = OrderedDict()
        d2 = OrderedDict([('var1',1)])
        b = time.time()
        for i in range(360000):
            d1.update(d2)
        e = time.time()
        logging.info('dict update: %ds' % (e-b))



if __name__ == '__main__':
    unittest.main()