import sys
sys.path.append('/Users/bitbook/Documents/PostGradCourses/MainProj/Spac/src')
import unittest
import numpy
import utils.ModelUtils as ModelUtils
import logging
import math
import models.Models as Models

class CTMCFromMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='CTMCFromMatrixTest.log',
                filemode='w')

    def testAT697F(self):
        ctmc = Models.AT697F
        for i in ctmc:
            logging.info(str(i))
            
    def testTestCTMCModel(self):
        ctmc = Models.TestCTMCModel
        for i in ctmc:
            logging.info(str(i))


if __name__ == '__main__':
    unittest.main()