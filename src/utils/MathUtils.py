# generate random variable from a exponential distribution
# given that it's less than t.
# e.g. implementation of forcing.
# if forcing is False, return normal random variable from the exponential distribution
# of the rate parameter set to be lamda.
def randomExpo(lamda, t=None, forcing=True):
    import random, math
    rnd = random.uniform(0, 1)
    if forcing and t:
        return math.log(1-rnd*(1-math.exp(-1*lamda*t)))/(-1*lamda)
    else:
        return math.log(1-rnd)/(-1*lamda)