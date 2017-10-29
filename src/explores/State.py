import os
curdir = os.getcwd()
pardir = os.path.dirname(os.path.abspath(curdir))
import sys
sys.path.append(pardir)
import random
import copy
import logging
import State
import ModulesFile

class State(object):

    def __init__(self, sid, localVars, modulesFile):
        self.stateId = sid
        self.localVars = localVars
        self.modulesFile = modulesFile
        self.apSet = set()
        self._fillInAPs()


    def __str__(self):
        result = 'State('
        for i,var in enumerate(self.localVars):
            if i == len(self.localVars)-1:
                result += '%s=%s' % (var.name, var.getValue())
            else:
                result += '%s=%s, ' % (var.name, var.getValue())
        result += ')'
        return result


    # check if ap holds at current state
    def checkAP(self, apName):
       return apName in self.apSet


    def _fillInAPs(self):
        if len(self.modulesFile.labels) == 0:
            return

        for name, func in self.modulesFile.labels.items():
            if func(self.modulesFile):
                self.apSet.add(name)


    # generate next possible state and holding time
    # in form of (holdingtime, PRISMState instance)
    # In DTMC case, holdingtime equals to 1
    # stateId: next State's Id
    def next(self, stateId):
        

        # logging.info([str(command) for command in enabledCommands])
        # logging.info([str(command.prob) for command in enabledCommands]) 
        exitRate = sum([command.prob for command in enabledCommands])
        probs = [command.prob/float(exitRate) for command in enabledCommands]

        rnd = random.random() # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                enabledCommand = enabledCommands[index]
                # logging.info('exec comm %s action. ' % enabledCommand.name)
                enabledCommand.execAction()
                holdingTime = random.expovariate(exitRate)
                if self.modulesFile.modelType == ModulesFile.ModelType.DTMC:
                    holdingtime = 1
                return (returned, holdingTime)

