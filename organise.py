#!/usr/bin/env python

"""Organise players in to cheaters and legit folders"""

import argparse
import sys
import os
import pickle
from modules.bcolors.bcolors import bcolors
from modules.api.api import get_player_data
from modules.api.tools import get_files

sys.setrecursionlimit(2000)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("token", metavar="TOKEN",
                    help="secret token for the lichess api")
settings = parser.parse_args()

"""Start importing players"""
def organise_training_data(token):
    unsorted_pkl = get_files('test-data/saved/')
    unsorted = {}
    for i in unsorted_pkl:
        with open('test-data/saved/'+i, 'rb') as inputpkl:
            d = pickle.load(inputpkl)
            player_data = get_player_data(d.name, token)
            if player_data['assessment']['user']['engine']:
                os.rename('test-data/saved/'+i, 'test-data/saved/cheaters/'+i)
            elif player_data['history'][0]['data'].get('processedBy', None) is not None:
                os.rename('test-data/saved/'+i, 'test-data/saved/legits/'+i)

#organise_training_data(settings.token)