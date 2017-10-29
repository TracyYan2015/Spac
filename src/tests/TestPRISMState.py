#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, filename = 'TestPRISMState.log', filemode='w')
import unittest
import os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir))
import sys
sys.path.append(parDir)
import explores.PRISMState as PRISMState
import explores.ModulesFile as ModulesFile
import time

class TestPRISMState(unittest.TestCase):
    # def testCreationPRISMState(self):
    #     modulesFile = ModulesFile.GYNCTMCModel()
    #     prismState = modulesFile.genPRISMState()
    #     # for var in prismState.localVars:
    #     #     print '%s = %s' % (var.name, var.getValue())

    # def testRandomPath(self):
    #     modulesFile = ModulesFile.GYNCTMCModel()
    #     MONTH = float(1.0/12*365*24*3600)
    #     YEAR = float(1.0*365*24*3600)
    #     duration1 = YEAR
    #     logging.info('generate path of duration: %s' % str(duration1) + 's')
    #     start = time.time()
    #     path = modulesFile.genRandomPath(duration1)
    #     end = time.time()
    #     logging.info('Time caused for generating path: %sS' % str(end-start))
    #     logging.info('Size of path: %sMB' % str(float(sys.getsizeof(path))/(1024*1024)))
    #     # logging.info('PATH, len=%d:' % len(path))
    #     # for state, time  in path:
    #         # logging.info(str(state) + ', holdingTime: ' + str(time))
    #     duration2 = sum([step[1] for step in path])
    #     self.assertAlmostEqual(duration1, duration2, delta=1.0)


    def testNextState(self):
        model = ModulesFile.GYNCTMCModel()
        ps = model.getModelInitState()
        nps,_ = ps.next()
        while True:
            if len(nps.convert2State().apSet) > 1:
                logging.info(str([str(var) for var in nps.localVars]))
                logging.info(str(nps.convert2State().apSet))
                break
            nps,_ = nps.nextPRISMState()


    



if __name__ == '__main__':
    unittest.main()