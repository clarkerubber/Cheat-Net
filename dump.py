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
from modules.bcolors.bcolors import bcolors
from modules.api.tools import get_files, get_player_games
from modules.analysis.tools import avg
from operator import itemgetter

sys.setrecursionlimit(2000)

try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

def dump_dir(dr, engine):
    in_pkl = get_files(dr)
    out = []
    for i in in_pkl:
        with open(dr+i, 'rb') as inputpkl:
            d = pickle.load(inputpkl)
            print d.name
            if len(d.flags()) > 1:
                print (tuple(list(round(i) for i in d.flags())), (int(engine),))
                out.append((tuple(d.flags()), (int(engine),)))
    return out

dump = dump_dir('test-data/saved/legits/', 0) + dump_dir('test-data/saved/cheaters/', 1)

with open('test-data/tensor_flags_dump.pkl', 'w+') as output:
    pickle.dump(dump, output, pickle.HIGHEST_PROTOCOL)