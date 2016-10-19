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
		print 'reading: '+str(i)
		cheaters[os.path.splitext(i)[0]] = pickle.load(inputpkl)

for i in legits_pkl:
	with open('test-data/saved/legits/'+i, 'rb') as inputpkl:
		print 'reading: '+str(i)
		legits[os.path.splitext(i)[0]] = pickle.load(inputpkl)

print 'LEGITS'
avgs = []
maxs = []
mins = []
for x, y in legits.items():
	print '   '+y.name+':'
	a = y.rank_5more_percents()
	try:
		maxim = max(a)
		minim = min(a)
		averg = avg(a)
		print 'max: '+str(maxim)
		print 'min: '+str(minim)
		print 'avg: '+str(averg)
		avgs.append(averg)
		maxs.append(maxim)
		mins.append(minim)
	except ValueError:
		pass
print 'max avg: '+str(max(avgs))
print 'min avg: '+str(min(avgs))
print 'max max: '+str(max(maxs))
print 'min min: '+str(min(mins))

print 'CHEATERS'
cheatscaught = 0
caught = []
notcaught = []
for x, y in cheaters.items():
	print '   '+y.name+':'
	a = y.rank_5more_percents()
	try:
		maxim = max(a)
		averg = avg(a)
		minim = min(a)
		print 'max: '+str(maxim)
		print 'min: '+str(minim)
		print 'avg: '+str(averg)
		if minim < min(mins) or averg < avg(avgs):
			print 'CAUGHT'
			cheatscaught += 1
			caught.append(y.name)
		else:
			notcaught.append(y.name)
	except ValueError:
		pass

print cheatscaught
print 'CAUGHT'
print caught
print 'NOT CAUGHT'
print notcaught