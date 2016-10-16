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
from modules.fishnet.fishnet import stockfish_command
from modules.bcolors.bcolors import bcolors
from modules.analysis.player import analyse_player
from modules.api.tools import get_files, get_player_games
from modules.analysis.tools import avg
from collections import Counter

import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.tools as tls
import numpy as np


try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

cheaters_pkl = get_files('test-data/saved/cheaters')
legits_pkl = get_files('test-data/saved/legits')

cheaters = {}
legits = {}

for i in cheaters_pkl:
	with open('test-data/saved/cheaters/'+i, 'rb') as inputpkl:
		cheaters[os.path.splitext(i)[0]] = pickle.load(inputpkl)

for i in legits_pkl:
	with open('test-data/saved/legits/'+i, 'rb') as inputpkl:
		legits[os.path.splitext(i)[0]] = pickle.load(inputpkl)

#legitavg = avg(sum(list(y.ranks() for x, y in legits.items()), []))
#cheateravg = avg(sum(list(y.ranks() for x, y in cheaters.items()), []))

#print 'legitavg: '+str(legitavg)
#print 'cheateravg: '+str(cheateravg)

print 'legits'
cp = 10
avgs = []
maxs = []
mins = []
for x, y in legits.items():
	#fig, ax = plt.subplots()
	#data = Counter(y.ranks())
	maxim = max(y.accuracy_percentages(cp))
	minim = min(y.accuracy_percentages(cp))
	averg = avg(y.accuracy_percentages(cp))
	print '   '+y.name+':'
	print 'max: '+str(maxim)
	print 'min: '+str(minim)
	print 'avg: '+str(averg)
	avgs.append(averg)
	maxs.append(maxim)
	mins.append(minim)
	#freqs = list(100*(sum(i == t for i in y.ranks())/float(len(y.ranks()))) for t in range(4)) + [100*sum(i > 3 for i in y.ranks())/len(y.ranks())]
	#ax.pie(freqs, labels=list(range(4))+['greater than 4'])
	#fig.show()
print 'max avg: '+str(max(avgs))
print 'min avg: '+str(min(avgs))
print 'max max: '+str(max(maxs))
print 'min min: '+str(min(mins))

print 'CHEATERS'
cheatscaught = 0
for x, y in cheaters.items():
	#fig, ax = plt.subplots()
	#data = Counter(y.ranks())
	maxim = max(y.accuracy_percentages(cp))
	averg = avg(y.accuracy_percentages(cp))
	minim = min(y.accuracy_percentages(cp))
	print '   '+y.name+':'
	print 'max: '+str(maxim)
	print 'min: '+str(minim)
	print 'avg: '+str(averg)
	if averg > max(avgs) or maxim < max(maxs):
		print 'CAUGHT'
		cheatscaught += 1
	#freqs = list(100*(sum(i == t for i in y.ranks())/float(len(y.ranks()))) for t in range(4)) + [100*sum(i > 3 for i in y.ranks())/len(y.ranks())]
	#ax.pie(freqs, labels=list(range(4))+['greater than 4'])
	#fig.show()
print cheatscaught
"""
fig, ax = plt.subplots()

for x, y in legits.items():
	xt, yt = y.error_v_move_no()
	ax.scatter(xt, yt, alpha=0.2)

fig.savefig('figures/legits/merged/ErrorVMoveNo.svg')


fig, ax = plt.subplots()

for x, y in cheaters.items():
	xt, yt = y.error_v_move_no()
	ax.scatter(xt, yt, alpha=0.2)

fig.savefig('figures/cheaters/merged/ErrorVMoveNo.svg')
"""