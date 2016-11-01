#!/usr/bin/env python

"""Analysing players for lichess.org"""

import argparse
import logging
import os
import sys
import pickle
from modules.bcolors.bcolors import bcolors
from modules.analysis.AnalysableGame import recent_games
from modules.analysis.AnalysedPlayer import AnalysedPlayer
from modules.analysis.PlayerAssessment import PlayerAssessment
from modules.api.tools import get_player_games, get_files
from modules.api.api import get_player_data, get_new_user_id, post_report

sys.setrecursionlimit(2000)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("token", metavar="TOKEN",
                    help="secret token for the lichess api")
parser.add_argument("file", metavar="FILE",
                    help="name of file to submit")
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


"""Start doing things"""

with open('neuralnet.pkl', 'r') as net_pkl:
    net = pickle.load(net_pkl)
    with open('test-data/saved/'+settings.file+'.pkl', 'rb') as input_pkl:
        player = pickle.load(input_pkl)
        post_report(player.name, player.assess_and_report(net), settings.token)
