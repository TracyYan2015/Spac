# contains transitionRateMatrix of each ctmc model in gyn essay
import numpy
import sys, os
curDir = os.getcwd()
parDir = os.path.abspath(os.path.dirname(curDir)+os.path.sep+".")
sys.path.append(parDir)
import utils.ModelUtils as ModelUtils

# AT697F module
rebootRate = 1.0/35
permanentDownRate = 1.0/(5*365*24*3600)
temporaryDownRate = 1.0/(12*3600)
AT697FMatrix = numpy.array([0,0,0,0,0,rebootRate,permanentDownRate,temporaryDownRate,0]).reshape(3,3)
apSetList = [set(['perm down']), set(['temp down']), set(['normal'])]
AT697F = ModelUtils.ctmcFromMatrix(AT697FMatrix, apSetList)

# test ctmc model
TestCTMCModelMatrix = numpy.array([0 ,1.5,0  ,0  ,
                                   3, 0,  1.5,0  ,
                                   0, 3,  0,  1.5,
                                   0, 0,  3,  0   ]).reshape(4,4)
apSetList2 = [set(['empty', 'default']), set(['default']), set(['default']), set(['full'])]
TestCTMCModel = ModelUtils.ctmcFromMatrix(TestCTMCModelMatrix, apSetList2)


