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
from modules.analysis.AnalysableGame import recent_games
from modules.analysis.AnalysedPlayer import AnalysedPlayer
from modules.analysis.PlayerAssessment import PlayerAssessment
from modules.api.tools import get_player_games
from modules.api.api import get_player_data, get_new_user_id, post_report

sys.setrecursionlimit(2000)

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


"""Start importing players"""

def collect_analyse_save(userId, net):
    try:
        player_data = get_player_data(userId, settings.token)
        playerAssessments = [PlayerAssessment(i) for i in player_data['assessment']['playerAssessments']]
        recents = recent_games(playerAssessments, player_data['games'])

        ap = AnalysedPlayer(
            userId, 
            recents, 
            player_data['assessment']['user']['games'], 
            player_data['assessment']['user']['engine'], 
            player_data['assessment']['relatedUsers'])

        [i.analyse(engine, info_handler) for i in ap.games]
        if ap.assess():
            logging.debug(bcolors.WARNING + userId + ' is likely cheating' + bcolors.ENDC)
            post_report(userId, ap.assess_and_report(net), settings.token)
        else:
            logging.debug(bcolors.WARNING + userId + ' is unlikely cheating' + bcolors.ENDC)
            post_report(userId, ap.assess_and_report(net), settings.token)

        with open('test-data/saved/'+userId+'.pkl', 'w+') as output:
            pickle.dump(ap, output, pickle.HIGHEST_PROTOCOL)
    except KeyError:
        logging.debug(bcolors.WARNING + userId + ' has no report information available' + bcolors.ENDC)
        post_report(userId, False, settings.token)

with open('neuralnet.pkl', 'r') as net_pkl:
    net = pickle.load(net_pkl)
    while True:
        collect_analyse_save(get_new_user_id(settings.token), net)