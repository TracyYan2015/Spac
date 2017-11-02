# -*- coding:utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from State import State
from Step import Step
import Module
from collections import OrderedDict
import time
import copy, random
import itertools
import sys


class ModelType:
    DTMC, CTMC = range(2)


# class represents a DTMC/CTMC model
class ModulesFile(object):

    # id used for generating State object when generating random path
    # should be added 1 whenever before self.nextState get called.
    _stateId = 0
 
    def __init__(self, modeltype):
        self.modules = OrderedDict()
        self.initLocalVars = OrderedDict() 
        self.localVars = OrderedDict()
        self.labels = dict()
        self.constants = dict()
        self.modelType = modeltype
        self.scDict = OrderedDict()
        self.curState = State(self._stateId, set())
        self.prevState = State(self._stateId, set())
        self.commPrepared = False

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

    # store new state's info in self.curState 
    # (e.g. the transition already happened)
    # store original state's info(localVars) in self.prevState
    def nextState(self):
        # get enabled commands list
        vars = [var.getValue() for _, var in self.localVars.items()]
        varsStr = ''.join([str(v) for v in vars])
        enabledCommands = self.scDict[varsStr]
        
        exitRate = sum([command.prob for command in enabledCommands])
        probs = [command.prob/float(exitRate) for command in enabledCommands]

        rnd = random.random()  # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                enabledCommand = enabledCommands[index]
                self.curState.updateAPs(self.localVars, self.constants, self.labels)
                self.prevState.stateId = self.curState.stateId
                self.prevState.apSet = self.curState.apSet.copy()
                enabledCommand.execAction()
                ModulesFile._stateId += 1
                self.curState.stateId = ModulesFile._stateId
                holdingTime = random.expovariate(exitRate)
                holdingTime = [1, holdingTime][self.modelType]
                return holdingTime

    # return list of Step instance
    # PAY ATTENTION THAT DEFINITION OF Step CLASS HAS CHANGED!
    # cachedPrefixes: # TODO how to implement?
    def genRandomPath(self, duration, cachedPrefixes=None):
        # Since when initilize a module, all its local variables
        # have been initilized
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True
        start = time.time()
        path = list()
        timeSum = 0.0
        passedTime = 0.0
        while timeSum < duration:
            holdingTime = self.nextState()
            timeSum += holdingTime
            if timeSum > duration:
                holdingTime -= (timeSum - duration)
            
            step = Step(self.prevState.stateId, self.prevState.apSet, holdingTime, passedTime)
            path.append(step)
            passedTime += holdingTime

        end = time.time()
        pathSize = sys.getsizeof(path)
        logging.info('Gen path of len %d and duration %ds.' % (len(path), duration))
        logging.info('Time caused: %ss' % str(end-start))
        logging.info('Memory caused: %fk' % float(sys.getsizeof(path)/1024))

        self.restoreStateId()
        self.restoreInitState()
        
        return False,path

    def getCurrentState(self):
        return self.curState

    def getModelInitState(self):
        return State(0, self.initLocalVars, self)

    def restoreInitState(self):
        self.localVars = self.initLocalVars
        self.initLocalVars = copy.copy(self.localVars)

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
        for _,module in self.modules.items():
            for _,command in module.commands.items():
                command.vs = self.localVars
                command.cs = self.constants

    def exportPathTo(self, path, filename):
        f = file(filename, 'w')
        f.write('stateId, apSet, passedTime, holdingTime\n')
        for step in path:
            f.write('%d, %s, %ss, %ss\n' % (step.stateId, str(step.apSet), step.passedTime, step.holdingTime))
        f.close()


def GYNCTMCModel():
    modulesFile = ModulesFile(ModelType.CTMC)
    modulesFile.addModule(Module.AT697F())
    modulesFile.addModule(Module.AX2000())
    modulesFile.addModule(Module.AFS600())
    modulesFile.addModule(Module.AT7910())
    modulesFile.addModule(Module.V5_FPGA())

    # !down & (m=1|d=1)
    # 发生瞬态故障
    def danger(vs, cs):
        m = vs['m'].getValue()
        d = vs['d'].getValue()
        return not down(vs, cs) and (m == 1 or d == 1)

    def down(vs, cs):
        count = vs['count'].getValue()
        MAX_COUNT = cs['MAX_COUNT']
        i = vs['i'].getValue()
        o = vs['o'].getValue()
        a = vs['a'].getValue()
        m = vs['m'].getValue()
        d = vs['d'].getValue()
        return i == 0 or count == (MAX_COUNT+1) or o == 0 or a == 0 or m == 0 or d == 0

        # !down & !danger
    def up(vs, cs):
        return not danger(vs, cs) and not down(vs, cs)

    modulesFile.addLabel('down', down)
    modulesFile.addLabel('danger', danger)
    modulesFile.addLabel('up', up)

    return modulesFile

