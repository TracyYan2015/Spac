#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, filename='TestCTMCChecker.log', filemode='w')
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.ModulesFile as ModulesFile
import explores.Module as Module
import time
import Checker

class CheckerTest(unittest.TestCase):
    def testCheckerUntil(self):
        # compute the probability of satisfy a until formula
        # YEAR = float(31536000)
        # MONTH = float(31*24*3600)
        # HOUR = float(3600)
        # model = ModulesFile.GYNCTMCModel()
        # csl = ['U[0,3600]', 'T', 'down']
        # checker = Checker.Checker(model = model, csl=csl, duration=HOUR, checkingType=1)
        # begin = time.time()
        # lowerBound, upperBound = checker.run()
        # end = time.time()
        # logging.info('Time caused to check the prob satisfying %s: %ss' % (str(end-begin), str(csl)))
        # logging.info('lowBound = %s, highBound = %s' % (str(lowerBound), str(upperBound)))
        pass

    def testSFB(self):
        ONEYEAR = float(365*24*3600)
        model = ModulesFile.BalancedModel()
        delta = 0.5
        model.SFB(delta)
        logging.info("delta parameter: %f" % delta)
        ltl = ['U[0,15768000]', 'T', 'failure'] # failure probability within one year
        checker = Checker.Checker(model=model, ltl=ltl, duration=ONEYEAR, checkingType=Checker.Checker.CheckingType.QUANTATIVE)
        begin = time.time()
        lowerbound, upperbound = checker.run()
        end = time.time()
        logging.info('Time caused: %s' % str(end - begin))
        logging.info('lowBound = %s, highBound = %s' % (str(lowerbound), str(upperbound)))


    def testBFB(self):
        model = ModulesFile.BalancedModel()
        delta = 0.5
        model.BFB(delta)
        def failure(vs, cs):
            return (vs['i'] == 0 and vs['di'] == 0) or vs['a'] == 0
        model.stopCondition = failure
        model.forcing = True
        ltl = ['U[0,5356800]', 'T', 'failure'] # failure probability within one month
        checker = Checker.Checker(model=model, ltl=ltl, duration=2678400*2, checkingType=Checker.Checker.CheckingType.QUANTATIVE)
        begin = time.time()
        lowerbound, upperbound = checker.run()
        end = time.time()
        logging.info('Time caused: %s' % str(end - begin))
        logging.info('lowBound = %s, highBound = %s' % (str(lowerbound), str(upperbound)))


    def testBFBOfToyModel(self):
        model = ModulesFile.toyModel()
        delta = 0.5
        model.BFB(delta)

        def failure(vs, cs):
            return vs['v'] == 0

        model.stopCondition = failure
        model.forcing = True
        ltl = ['U[0,2000000]', 'T', 'failure']  # failure probability within 25 time units
        checker = Checker.Checker(model=model, ltl=ltl, duration=2000000,
                                  checkingType=Checker.Checker.CheckingType.QUANTATIVE)
        begin = time.time()
        lowerbound, upperbound = checker.run()
        end = time.time()
        logging.info('Time caused: %s' % str(end - begin))
        # logging.info('lowBound = %s, highBound = %s' % (str(lowerbound), str(upperbound)))

    def testUpperBound(self):
        # test method for interval unreliability estimation for large time horizon
        # compare the upper bound with the real value to see if they are almost equal.
        failurerate = Module.failrate
        for i in range(1, 7):
            if i > 1:
                ratio = float(i-1)/i
                Module.failrate *= ratio
            model = ModulesFile.BalancedModel()
            delta = 0.5
            model.BFB(delta)
            model.forcing = False

            def failure(vs, cs):
                return (vs['i'] == 0 and vs['di'] == 0) or (vs['a'] == 0 and vs['da'] == 0)

            def allUp(vs, cs):
                return vs['i'] == 1 and vs['di'] == 1 and vs['a'] == 1 and vs['da'] == 1

            def stopCondition(vs, cs):
                return failure(vs, cs) or allUp(vs, cs)

            model.stopCondition = stopCondition
            ltl = None
            ONEYEAR = 365*24*3600
            checker = Checker.Checker(model=model, ltl=ltl, duration=ONEYEAR, checkingType=Checker.Checker.CheckingType.QUANTATIVE)
            begin = time.time()
            upperBound = checker.intervalUnreliability(ONEYEAR)
            logging.info('i=%d, upperBound = %s' % (i, str(upperBound)))
            end = time.time()
            logging.info("time: %s" % str(end -begin))




if __name__ == '__main__':
    unittest.main()