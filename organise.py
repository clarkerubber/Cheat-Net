#!/usr/bin/env python

"""Organise players in to cheaters and legit folders"""

import argparse
import sys
import os
import pickle
from modules.bcolors.bcolors import bcolors
from modules.api.api import get_player_data
from modules.api.tools import get_files
from operator import attrgetter

"""Start importing players"""
def organise_training_data(token):
    unsorted_pkl = get_files('test-data/saved/')
    unsorted = {}
    for i in unsorted_pkl:
        with open('test-data/saved/'+i, 'rb') as inputpkl:
            d = pickle.load(inputpkl)
            player_data = get_player_data(d.name, token)
            processed = list([x for x in player_data['history'] if x['type'] == 'report'])[0].get('processedBy', None) is not None
            if player_data['assessment']['user']['engine']:
                os.rename('test-data/saved/'+i, 'test-data/saved/cheaters/'+i)
            elif processed:
                os.rename('test-data/saved/'+i, 'test-data/saved/legits/'+i)

#organise_training_data(settings.token)