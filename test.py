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

def analyse_pkl(dr, pkl_names, net):
	maxim = 0
	marked = []
	unmarked = []
	for i in pkl_names:
		with open(dr+i, 'rb') as inputpkl:
			p = pickle.load(inputpkl)
			assessment = p.assess(net)
			activation = round(p.activation(net), 3)
			report = p.report(net)
			if activation > maxim:
				maxim = activation
			if assessment:
				marked.append((p.name, activation))
			else:
				unmarked.append((p.name, activation))
	print 'Maxim: '+str(maxim)
	print 'MARKED'
	print len(marked)
	print marked
	print 'UNMARKED'
	print len(unmarked)
	print unmarked

with open('neuralnet.pkl', 'r') as net_pkl:
	net = pickle.load(net_pkl)
	print 'LEGITS'
	analyse_pkl('test-data/saved/legits/', legits_pkl, net)
	print ''
	print 'CHEATERS'
	analyse_pkl('test-data/saved/cheaters/', cheaters_pkl, net)