from operator import attrgetter

import numpy as np

def avg(l, default = 0):
    if len(l) > 0:
        return sum(l) / float(len(l))
    else:
        return default

def bounded_eval(e):
    return min(1000, max(-1000, e))

def scaled_eval(e):
    return 2 / (1 + np.exp(-0.005 * e)) - 1
