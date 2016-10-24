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
    avgweights = {'mb': 0, 'hb': 0, 'ho': 0, 'mt': 0, 'mbmt': 0, 'hbmt': 0, 'homt': 0}
    for flag, val in weights.items():
        while not max(func(averg = averg, maxim = maxim, weights = weights, avgweights = {}) or [0]) > 0 and weights[flag] < 100:
            weights[flag] += 1
        weights[flag] -= 1
    for flag, val in avgweights.items():
        while not max(func(averg = averg, maxim = maxim, weights = {}, avgweights = avgweights) or [0]) > 0 and avgweights[flag] < 100:
            avgweights[flag] += 1
        avgweights[flag] -= 1
    return (weights, avgweights)

def minimise_weights(weights): # Find the maximum weight allowed to not mark any legit players
    weights_output = {'mb': 100, 'hb': 100, 'ho': 100, 'mt': 100, 'mbmt': 100, 'hbmt': 100, 'homt': 100}
    for w in weights:
        for key, val in w.items():
            if weights_output[key] > val:
                weights_output[key] = val
    return weights_output

def max_and_avg(func): # used to find the maximum averg and max values while not marking a legit player
    averg = 100
    while not max(func(averg = averg, maxim = 100, weights = {}, avgweights = {}) or [0]) > 0 and averg > 0:
        averg -= 1
    averg += 1
    maxim = 100
    while not max(func(averg = 100, maxim = maxim, weights = {}, avgweights = {}) or [0]) > 0 and maxim > 0:
        maxim -= 1
    maxim += 1
    return (maxim, averg)



r0p_mxavgs = []
r1p_mxavgs = []
r01p_mxavgs = []
r5lp_mxavgs = []
r0m20p_mxavgs = []
c20_mxavgs = []
c10_mxavgs = []

ag150_10 = []
ag200_30 = []
sag150_10 = []
sag200_30 = []
for x, y in legits.items():
    r0p_mxavgs.append(max_and_avg(y.assess_rank_0_percents))
    r1p_mxavgs.append(max_and_avg(y.assess_rank_1_percents))
    r01p_mxavgs.append(max_and_avg(y.assess_rank_01_percents))
    r5lp_mxavgs.append(max_and_avg(y.assess_rank_5less_percents))
    r0m20p_mxavgs.append(max_and_avg(y.assess_rank_0_move20plus_percents))
    c20_mxavgs.append(max_and_avg(y.assess_cpl20_percents))
    c10_mxavgs.append(max_and_avg(y.assess_cpl10_percents))

    if len(y.games) > 2:
        ag150_10.append(y.accuracy_given_advantage(advantage = 150, threshold = 10))
        sag150_10.append(y.accuracy_given_scaled_advantage(scaled_advantage = 150, scaled_threshold = 10))
        ag200_30.append(y.accuracy_given_advantage(advantage = 200, threshold = 30))
        sag200_30.append(y.accuracy_given_scaled_advantage(scaled_advantage = 200, scaled_threshold = 30))

r0p_max = max(r0p_mxavgs, key=itemgetter(0))[0]
r0p_avg = max(r0p_mxavgs, key=itemgetter(1))[1]

r1p_max = max(r1p_mxavgs, key=itemgetter(0))[0]
r1p_avg = max(r1p_mxavgs, key=itemgetter(1))[1]

r01p_max = max(r01p_mxavgs, key=itemgetter(0))[0]
r01p_avg = max(r01p_mxavgs, key=itemgetter(1))[1]

r5lp_max = max(r5lp_mxavgs, key=itemgetter(0))[0]
r5lp_avg = max(r5lp_mxavgs, key=itemgetter(1))[1]

r0m20p_max = max(r0m20p_mxavgs, key=itemgetter(0))[0]
r0m20p_avg = max(r0m20p_mxavgs, key=itemgetter(1))[1]

c20_max = max(c20_mxavgs, key=itemgetter(0))[0]
c20_avg = max(c20_mxavgs, key=itemgetter(1))[1]

c10_max = max(c10_mxavgs, key=itemgetter(0))[0]
c10_avg = max(c10_mxavgs, key=itemgetter(1))[1]


r0p_weights = []
r1p_weights = []
r01p_weights = []
r5lp_weights = []
r0m20p_weights = []
c20_weights = []
c10_weights = []
for x, y in legits.items():
    r0p_weights.append(maximise_weights(y.assess_rank_0_percents, r0p_avg, r0p_max))
    r1p_weights.append(maximise_weights(y.assess_rank_1_percents, r1p_avg, r1p_max))
    r01p_weights.append(maximise_weights(y.assess_rank_01_percents, r01p_avg, r01p_max))
    r5lp_weights.append(maximise_weights(y.assess_rank_5less_percents, r5lp_avg, r5lp_max))
    r0m20p_weights.append(maximise_weights(y.assess_rank_0_move20plus_percents, r0m20p_avg, r0m20p_max))
    c20_weights.append(maximise_weights(y.assess_cpl20_percents, c20_avg, c20_max))
    c10_weights.append(maximise_weights(y.assess_cpl10_percents, c20_avg, c10_max))

print 'ACCURACY GIVEN ADV 150 10'
print str(max(ag150_10))+"\n"

print 'SCALED ACCURACY GIVEN ADV 150 10'
print str(max(sag150_10))+"\n"

print 'ACCURACY GIVEN ADV 200 30'
print str(max(ag200_30))+"\n"

print 'SCALED ACCURACY GIVEN ADV 200 30'
print str(max(sag200_30))+"\n"

print 'RANK 0 PERCENTS'
print '            averg = '+str(r0p_avg)+','
print '            maxim = '+str(r0p_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in r0p_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in r0p_weights)))+"\n"

print 'RANK 1 PERCENTS'
print '            averg = '+str(r1p_avg)+','
print '            maxim = '+str(r1p_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in r1p_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in r1p_weights)))+"\n"

print 'RANK 01 PERCENTS'
print '            averg = '+str(r01p_avg)+','
print '            maxim = '+str(r01p_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in r01p_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in r01p_weights)))+"\n"

print 'RANK 5 LESS PERCENTS'
print '            averg = '+str(r5lp_avg)+','
print '            maxim = '+str(r5lp_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in r5lp_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in r5lp_weights)))+"\n"

print 'RANK 0 MOVE 20+ PERCENTS'
print '            averg = '+str(r0m20p_avg)+','
print '            maxim = '+str(r0m20p_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in r0m20p_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in r0m20p_weights)))+"\n"

print 'CPL <20 PERCENTS'
print '            averg = '+str(c20_avg)+','
print '            maxim = '+str(c20_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in c20_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in c20_weights)))+"\n"

print 'CPL <10 PERCENTS'
print '            averg = '+str(c10_avg)+','
print '            maxim = '+str(c10_max)+','
print '            weights = '+str(minimise_weights(list(i[0] for i in c10_weights)))+','
print '            avgweights = '+str(minimise_weights(list(i[1] for i in c10_weights)))+"\n"