#!/usr/bin/env python

"""Analysing players for lichess.org"""

import argparse
import chess
import chess.uci
import chess.pgn
import logging
import os
import sys
import pickle
from modules.analysis.AnalysedPlayer import AnalysedPlayer
from modules.fishnet.fishnet import stockfish_command
from modules.bcolors.bcolors import bcolors
from modules.api.tools import get_files, get_player_games
from modules.analysis.tools import avg
from operator import itemgetter

try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

# Import Legits
legits_pkl = get_files('test-data/saved/legits')
legits = {}
for i in legits_pkl:
    with open('test-data/saved/legits/'+i, 'rb') as inputpkl:
        print 'reading: '+str(i)
        legits[os.path.splitext(i)[0]] = pickle.load(inputpkl)

def maximise_weights(func, averg, maxim): # used to find the maximum weight value while not marking a legit player
    weights = {'mb': 0, 'hb': 0, 'ho': 0, 'mt': 0, 'mbmt': 0, 'hbmt': 0, 'homt': 0}
    for flag, val in weights.items():
        while not func(averg = averg, maxim = maxim, weights = weights) and weights[flag] < 100:
            weights[flag] += 1
        weights[flag] -= 1
    return weights

def minimise_weights(weights): # Find the maximum weight allowed to not mark any legit players
    weights_output = {'mb': 100, 'hb': 100, 'ho': 100, 'mt': 100, 'mbmt': 100, 'hbmt': 100, 'homt': 100}
    for w in weights:
        for key, val in w.items():
            if weights_output[key] > val:
                weights_output[key] = val
    return weights_output

def max_and_avg(func): # used to find the maximum averg and max values while not marking a legit player
    averg = 100
    while not func(averg = averg, maxim = 100, weights = {}) and averg > 0:
        averg -= 1
    averg += 1
    maxim = 100
    while not func(averg = 100, maxim = maxim, weights = {}) and maxim > 0:
        maxim -= 1
    maxim += 1
    return (maxim, averg)

r0p_mxavgs = []
r01p_mxavgs = []
r5lp_mxavgs = []
r0m20p_mxavgs = []
c20_mxavgs = []
for x, y in legits.items():
    r0p_mxavgs.append(max_and_avg(y.assess_rank_0_percents))
    r01p_mxavgs.append(max_and_avg(y.assess_rank_01_percents))
    r5lp_mxavgs.append(max_and_avg(y.assess_rank_5less_percents))
    r0m20p_mxavgs.append(max_and_avg(y.assess_rank_0_move20plus_percents))
    c20_mxavgs.append(max_and_avg(y.assess_cpl20_percents))

r0p_max = max(r0p_mxavgs, key=itemgetter(0))[0]
r0p_avg = max(r0p_mxavgs, key=itemgetter(1))[1]

r01p_max = max(r01p_mxavgs, key=itemgetter(0))[0]
r01p_avg = max(r01p_mxavgs, key=itemgetter(1))[1]

r5lp_max = max(r5lp_mxavgs, key=itemgetter(0))[0]
r5lp_avg = max(r5lp_mxavgs, key=itemgetter(1))[1]

r0m20p_max = max(r0m20p_mxavgs, key=itemgetter(0))[0]
r0m20p_avg = max(r0m20p_mxavgs, key=itemgetter(1))[1]

c20_max = max(c20_mxavgs, key=itemgetter(0))[0]
c20_avg = max(c20_mxavgs, key=itemgetter(1))[1]


r0p_weights = []
r01p_weights = []
r5lp_weights = []
r0m20p_weights = []
c20_weights = []
for x, y in legits.items():
    r0p_weights.append(maximise_weights(y.assess_rank_0_percents, r0p_avg, r0p_max))
    r01p_weights.append(maximise_weights(y.assess_rank_01_percents, r01p_avg, r01p_max))
    r5lp_weights.append(maximise_weights(y.assess_rank_5less_percents, r5lp_avg, r5lp_max))
    r0m20p_weights.append(maximise_weights(y.assess_rank_0_move20plus_percents, r0m20p_avg, r0m20p_max))
    c20_weights.append(maximise_weights(y.assess_cpl20_percents, c20_avg, c20_max))

print 'RANK 0 PERCENTS'
print '  AVG: '+str(r0p_avg)
print '  MAX: '+str(r0p_max)
print '  WEIGHTS: '+str(minimise_weights(r0p_weights))

print 'RANK 01 PERCENTS'
print '  AVG: '+str(r01p_avg)
print '  MAX: '+str(r01p_max)
print '  WEIGHTS: '+str(minimise_weights(r01p_weights))

print 'RANK 5 LESS PERCENTS'
print '  AVG: '+str(r5lp_avg)
print '  MAX: '+str(r5lp_max)
print '  WEIGHTS: '+str(minimise_weights(r5lp_weights))

print 'RANK 0 MOVE 20+ PERCENTS'
print '  AVG: '+str(r0m20p_avg)
print '  MAX: '+str(r0m20p_max)
print '  WEIGHTS: '+str(minimise_weights(r0m20p_weights))

print 'CPL <20 PERCENTS'
print '  AVG: '+str(c20_avg)
print '  MAX: '+str(c20_max)
print '  WEIGHTS: '+str(minimise_weights(c20_weights))