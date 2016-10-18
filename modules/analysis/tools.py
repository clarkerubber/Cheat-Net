from operator import attrgetter

def avg(l):
    if len(l) > 0:
        return sum(l) / float(len(l))
    else:
        return 0

def bounded_eval(e):
    return min(1000, max(-1000, e))