# -*- coding:utf-8 -*-
import logging
# logging.basicConfig(level=logging.DEBUG, filename='ModulesFileGenPath.log', filemode='w')
logging.basicConfig(level=logging.DEBUG)
from State import State
from Step import Step
import Module
from collections import OrderedDict
import time
import copy, random
import itertools


class ModelType:
    DTMC, CTMC = range(2)

# class represents a DTMC/CTMC model
class ModulesFile(object):

    # id used for generating State object when generating random path
    _stateId = 0
 
    def __init__(self, modelType):
        self.modules = OrderedDict()
        self.initLocalVars = OrderedDict() 
        self.localVars = OrderedDict()
        self.labels = dict()
        self.constants = dict()
        self.modelType = modelType
        self.scDict =  OrderedDict()

    # module: module instance
    def addModule(self, module):
        self.modules[module.name] = module
        # add variables
        for k,v in module.variables.items():
            self.localVars[k] = v
        for k,v in module.variables.items():
            self.initLocalVars[k] = copy.copy(v)
        # add constants
        self.constants.update(module.constants)
        module.modulesFile = self

    def getModuleByName(self, name):
        if name in self.modules.keys():
            return self.modules[name]
        return None

    # get module's local variables
    # if the variable cannot be found, return None
    # For now, let's assume there are no variables with same name in 
    # different modules
    def getLocalVar(self, varName='', moduleName=''):
        return self.localVars[varName]

    # For now, let's assume there are no constant with same name in 
    # different modules
    def getConstant(self, name='', moduleName=''):
        return self.constants[name]


    # label: a function represents ap
    # label is implemented as a function object that receive
    # ModulesFile instance as the parameter
    def addLabel(self, name, label):
        self.labels[name] = label

    # generate a State instance according to current 
    # localVars
    def genState(self):
        return State(self._stateId, self.localVars, self)

    def nextState(self):
        enabledCommands = list()
        if len(self.scDict) > 0:
            varTuple = tuple([var.getValue() for _,var in self.localVars.items()])
            varsStr = ''.join([str(v) for v in varTuple])
            enabledCommands = self.scDict[varsStr]
            # logging.info('cache hit')

        if len(enabledCommands) == 0:
            for _,module in self.modules.items():
                for _,command in module.commands.items():
                    command.vs = self.localVars
                    command.cs = self.constants
                    if command.evalGuard():
                        enabledCommands.append(command)
            logging.info('cache not hit')
        
        exitRate = sum([command.prob for command in enabledCommands])
        probs = [command.prob/float(exitRate) for command in enabledCommands]

        rnd = random.random() # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                enabledCommand = enabledCommands[index]
                enabledCommand.execAction()
                holdingTime = random.expovariate(exitRate)
                if self.modelType == ModelType.DTMC:
                    holdingtime = 1
                return (self.getCurrentState(), holdingTime)


    # return list of Step instance
    # PAY ATTENTION THAT DEFINITION OF Step CLASS HAS CHANGED!
    # cachedPrefixes: # TODO how to implement?
    def genRandomPath(self, duration, cachedPrefixes=None):
        # Since when initilize a module, all its local variables
        # have been initilized
        logging.info('Starting generating random path.')
        start = time.time()
        path = list()
        curState = self.getCurrentState()
        ModulesFile._stateId += 1
        timeSum = 0.0
        passedTime = 0.0
        # logging.info('PATH:')
        while timeSum < duration:
            (_nextState, holdingTime) = self.nextState()
            self._stateId += 1
            timeSum += holdingTime
            if timeSum > duration:
                holdingTime = holdingTime - (timeSum - duration)

            # logging.info('time cumul: ' + str(timeSum))
            
            step = Step(curState.stateId, curState.apSet, holdingTime, passedTime)
            path.append(step)
            passedTime += holdingTime
            curState = _nextState

        end = time.time()
        logging.info('Gen path of len %d and duration %ds.' % (len(path), duration))
        logging.info('Time caused: %ss' % str(end-start))

        self.restoreStateId()
        self.restoreInitState()
        
        return (False,path)

    def getCurrentState(self):
        return State(self._stateId, self.localVars, self)

    def getModelInitState(self):
        return State(self._stateId, self.localVars, self)
        

    def restoreInitState(self):
        self.localVars = self.initLocalVars

    def restoreStateId(self):
        self._stateId = 0


    # generate enabled commands for each state of the model beforehand
    # to accelerate the speed of generating random path
    def prepareCommands(self):
        vsCpy = OrderedDict()
        for k,v in self.localVars.items():
            vsCpy[k] = copy.copy(v)
        for vsList in itertools.product(*[v.allVarsList() for _,v in vsCpy.items()]):
            vsDict = OrderedDict()
            for v in vsList:
                vsDict[v.name] = v
            enabledCommands = list()
            for _,module in self.modules.items():
                for _,command in module.commands.items():
                    command.vs = vsDict
                    command.cs = self.constants
                    if command.evalGuard():
                        enabledCommands.append(command)
            varTuple = tuple([item[1].getValue() for item in vsDict.items()])
            varsStr = ''.join([str(v) for v in varTuple])
            self.scDict[varsStr] = enabledCommands

def GYNCTMCModel():
    modulesFile = ModulesFile(ModelType.CTMC)
    modulesFile.addModule(Module.AT697F())
    modulesFile.addModule(Module.AX2000())
    modulesFile.addModule(Module.AFS600())
    modulesFile.addModule(Module.AT7910())
    modulesFile.addModule(Module.V5_FPGA())

    # 发生永久故障
    def down(modulesFile):
            count = modulesFile.getLocalVar('count')
            MAX_COUNT = modulesFile.getConstant('MAX_COUNT')
            i = modulesFile.getLocalVar('i')
            o = modulesFile.getLocalVar('o')
            a = modulesFile.getLocalVar('a')
            m = modulesFile.getLocalVar('m')
            d = modulesFile.getLocalVar('d')
            return i == 0 or count ==  (MAX_COUNT+1) or o == 0 or a == 0 or m == 0 or d == 0

    modulesFile.addLabel('down', down)

    # !down & (m=1|d=1)
    # 发生瞬态故障
    def danger(modulesFile):
        m = modulesFile.getLocalVar('m')
        d = modulesFile.getLocalVar('d')
        return not down(modulesFile) and (m == 1 or d == 1)

    modulesFile.addLabel('danger', danger)

    # !down & !danger
    def up(modulesFile):
        return not danger(modulesFile) and not down(modulesFile)

    modulesFile.addLabel('up', up)
#     set(['down', 'up'])
# ['(d = 2)', '(count = 2)', '(m = 2)', '(i = 1)', '(a = 1)', '(o = 1)']
    return modulesFile

