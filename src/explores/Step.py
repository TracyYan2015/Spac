class Step(object):
    def __init__(self, stateId, apSet, holdingTime, passedTime):
        # current state's stateId before transition happen
        self.stateId = stateId
        # current state's apSet of State before transition happen
        self.apSet = apSet
        # time duration before transfer to next state
        self.holdingTime = holdingTime
        # time(steps) passed before entering current state
        self.passedTime = passedTime

    def __str__(self):
        return '( ' + str(self.apSet) + ', ' + str(self.holdingTime) + 's )'
