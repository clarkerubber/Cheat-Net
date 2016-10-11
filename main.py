#!/usr/bin/env python

"""Analysing players for lichess.org"""

import argparse
import chess
import chess.uci
import chess.pgn
import logging
import os
import sys
from modules.fishnet.fishnet import stockfish_command
from modules.bcolors.bcolors import bcolors
from modules.analysis.player import analyse_player
from modules.api.tools import get_folders, get_player_games

import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.tools as tls
import numpy as np

tls.set_credentials_file(username='Clarkey', api_key='jjln8tgi44')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("token", metavar="TOKEN",
                    help="secret token for the lichess api")
parser.add_argument("threads", metavar="THREADS", nargs="?", type=int, default=4,
                    help="number of engine threads")
parser.add_argument("memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                    help="memory in MB to use for engine hashtables")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
settings = parser.parse_args()

try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
logging.getLogger("chess.uci").setLevel(logging.WARNING)

engine = chess.uci.popen_engine(stockfish_command())
engine.setoption({'Threads': settings.threads, 'Hash': settings.memory})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

cheaters = get_folders('test-data/games/cheaters')
legits = get_folders('test-data/games/legits')

#for player in cheaters:
for i, p in enumerate(legits):
    print str(i) + ': ' + str(p)

for player in (cheaters):
    analyse_player(player[0], get_player_games(player[1]), engine, info_handler)
    ap.graph_games_all()