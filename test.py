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
from collections import Counter

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

with open('neuralnet.pkl', 'r') as net_pkl:
	net = pickle.load(net_pkl)
	print 'LEGITS'
	print 'Incorrectly Marked'
	incorrect = [y.name for x, y in legits.items() if y.assess(net) == 2]
	print len(incorrect)
	print incorrect
	print 'Correctly Ignored'
	correct = [y.name for x, y in legits.items() if y.assess(net) == 0]
	print len(correct)
	print correct
	print 'Indeterminate'
	unsure = [y.name for x, y in legits.items() if y.assess(net) == 1]
	print len(unsure)
	print unsure

	print ''
	print 'CHEATERS'
	print 'Correctly Marked'
	correct = [y.name for x, y in cheaters.items() if y.assess(net) == 2]
	print len(correct)
	print correct
	print 'Incorrectly Ignored'
	missed = [y.name for x, y in cheaters.items() if y.assess(net) == 0]
	print len(missed)
	print missed
	print 'Indeterminate'
	unsure = [y.name for x, y in cheaters.items() if y.assess(net) == 1]
	print len(unsure)
	print unsure