from operator import attrgetter

import math

def avg(l, default = 0):
    l = [i for i in l if i is not None]
    if len(l) > 0:
        return sum(l) / float(len(l))
    else:
        return default

def bounded_eval(e):
    return min(1000, max(-1000, e))

def scaled_eval(e):
    try:
        return 2 / (1 + math.exp(-0.005 * e)) - 1
    except OverflowError:
        return e
