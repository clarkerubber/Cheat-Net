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

print 'LEGITS'
print 'Incorrectly Marked'
incorrect = [y.name for x, y in legits.items() if y.assess()]
print len(incorrect)
print incorrect
correct = [y.name for x, y in legits.items() if not y.assess()]
print 'Correctly Ignored'
print len(correct)
print [y.name for x, y in legits.items() if not y.assess()]


print ''
print 'CHEATERS'
print 'Correctly Marked'
correct = [y.name for x, y in cheaters.items() if y.assess()]
print len(correct)
print correct
print 'Missed'
missed = [y.name for x, y in cheaters.items() if not y.assess()]
print len(missed)
print missed