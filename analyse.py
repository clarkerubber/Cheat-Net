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
from modules.analysis.AnalysableGame import recent_games
from modules.fishnet.fishnet import stockfish_command
from modules.bcolors.bcolors import bcolors
from modules.analysis.AnalysedPlayer import AnalysedPlayer
from modules.analysis.PlayerAssessment import PlayerAssessment

from modules.api.tools import get_folders, get_player_games
from modules.api.api import get_player_data

import matplotlib.pyplot as plt
import numpy as np

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

cheaters = [
    'IMSomeOne',
    'Variogram',
    'TrapidFred',
    'toraman71',
    'strongulos',
    'langarita',
    'ahmedxchess',
    'Paxirs',
    'envahisseur',
    'gregtraurig20',
    'toroman71',
    'kitabkurdu',
    'George_83',
    'ladyknight246',
    'keti',
    'beastchessorg',
    'sailsheets',
    'Psych0Che55',
    'Banga-nga-sexy',
    'eric092',
    'allaboutthechess',
    'duduh',
    'locego',
    'rodrigolmr',
    'poxyi',
    'Dzaquan',
    'mlakmostafa2000',
    'NihilDeNada',
    'Akramins',
    'Archimboldo',
    'Hyperiel',
    'Iolandactanduva',
    'MF_marrone',
    'Mnaaaa',
    'On_Fire21',
    'TheSindar',
    'blaastercr',
    'bmw318',
    'deepbobby',
    'drmirzaee2554',
    'eragon47',
    'fenerlitugi',
    'ggeftNakamura',
    'grefusa',
    'marrone1_744',
    'pilarsevilla',
    'rahola17',
    'twitchtvMimii'
]

legits = [
    'ChessJuice',
    'BeepBeepImAJeep',
    'Blitzstream-twitch',
    'Elda64',
    'Fanatist',
    'GnarlyGoat',
    'chesskm8',
    'Iamyourfather',
    'Kingscrusher-YouTube',
    'Lance5500',
    'Maci',
    'MeneerMandje',
    'Paramos',
    'Sparklehorse',
    'TVEDAS',
    'andrewrun',
    'berval',
    'blitzbullet',
    'chessclinic',
    'darkghoul',
    'juanarmando',
    'lovlas',
    'penguingim1',
    'BahadirOzen',
    'NobodyReally',
    'arna',
    'IMAndrasToth',
    'VNeustroev',
    'OhNoMyPants',
    'Darkhourse92',
    'RebeccaHarris',
    'opperwezen',
    'mostrovski',
    'AstanehChess',
    'FraGer68',
    'GnarlyGoat'
]

def collect_analyse_save(userId, cheater):
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

        dr = 'legits'
        if cheater:
            dr = 'cheaters'

        with open('test-data/saved/'+dr+'/'+userId+'.pkl', 'w+') as output:
            pickle.dump(ap, output, pickle.HIGHEST_PROTOCOL)
    except KeyError:
        pass

#[collect_analyse_save(userId, True) for userId in cheaters]
[collect_analyse_save(userId, False) for userId in legits[13:]]
