#!/usr/bin/env python

"""Organise player data into CSV format for processing by TensorFlow"""

import argparse
import pickle
import csv
import sys
from modules.analysis.AnalysedPlayer import AnalysedPlayer
from modules.api.tools import get_files
from modules.api.api import get_player_data

def add_row(writer, ap, status, token):
    for g in ap.flags():
        for x, _ in enumerate(g):
            g[x] = round(g[x], 3)
        if len(g) == 11:
            writer.writerow([int(status), ap.name] + g)

def dump_csv_training_data(token):
    legits_pkl = get_files('test-data/saved/legits')
    cheaters_pkl = get_files('test-data/saved/cheaters')

    with open('test-data/player_single_game_data.csv', 'wb') as fh:
        writer = csv.writer(fh, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['cheating', 'name', 'titled', 'mb1', 'h1','m1', 's1', 'r01', 'r11', 'cp201', 'cp101', 'cpar11', 'cpar21'])
        for i in legits_pkl:
            try:
                with open('test-data/saved/legits/'+i, 'rb') as ap_f:
                    print i
                    ap = pickle.load(ap_f)
                    add_row(writer, ap, False, token)
            except EOFError:
                pass
        for i in cheaters_pkl:
            try:
                with open('test-data/saved/cheaters/'+i, 'rb') as ap_f:
                    print i
                    ap = pickle.load(ap_f)
                    add_row(writer, ap, True, token)
            except EOFError:
                pass

if __name__ == "__main__":
    sys.setrecursionlimit(2000)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("token", metavar="TOKEN",
        help="secret token for the lichess api")
    settings = parser.parse_args()
    dump_csv_training_data(settings.token)