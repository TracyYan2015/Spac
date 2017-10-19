import CheckerCTMC

# transitionRateMatrix: ctmc transition rate matrix
# apSetList: list of apSet for each row of matrix(each State)
def ctmcFromMatrix(transitionRateMatrix, apSetList):
    ctmc = []
    for rowIndex, row in enumerate(transitionRateMatrix):
        state = CheckerCTMC.State(rowIndex)
        state.postStates = list() # solve the default parameters problem
        state.apSet = set()
        ctmc.append(state)

    for rowIndex, row in enumerate(transitionRateMatrix):
        for colIndex, col in enumerate(row):
            if col > 0:
                ctmc[rowIndex].postStates.append((ctmc[colIndex], col))

    for (apSet, state) in zip(apSetList, ctmc):
        state.apSet = apSet
    ctmc.insert(0, len(transitionRateMatrix))

    return ctmc