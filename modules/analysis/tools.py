from operator import attrgetter

import math

def avg(l, default = 0):
    l = [i for i in l if i is not None]
    if len(l) > 0:
        return sum(l) / float(len(l))
    else:
        return default

def weighted_avg(itergames, weights):
    return avg(list((r + weights_mask(weights, mb, hb, ho, mt)) for r, mb, hb, ho, mt in itergames))

def bounded_eval(e):
    return min(1000, max(-1000, e))

def scaled_eval(e):
    try:
        return 2 / (1 + math.exp(-0.005 * e)) - 1
    except OverflowError:
        return e

def weights_mask(weights, mb, hb, ho, mt):
    mod = [0]
    if mb:
        mod.append(weights.get('mb', 0))
    if hb:
        mod.append(weights.get('hb', 0))
    if ho:
        mod.append(weights.get('ho', 0))
    if mt:
        mod.append(weights.get('mt', 0))
    if mb and mt:
        mod.append(weights.get('mbmt', 0))
    if hb and mt:
        mod.append(weights.get('hbmt', 0))
    if ho and mt:
        mod.append(weights.get('homt', 0))
    return max(mod)