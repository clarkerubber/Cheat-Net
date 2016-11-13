#!/usr/bin/env python

"""Organise player data into CSV format for processing by TensorFlow"""

import argparse
import pickle
import csv
from modules.api.tools import get_files
from modules.api.api import get_player_data

def add_row(writer, ap, status, token):
    player_data = get_player_data(ap.name, token)
    related_players = len(player_data['assessment']['relatedUsers'])
    related_cheaters = len(player_data['assessment']['relatedCheaters'])

    try:
        c_to_l = related_cheaters/float(related_players)
    except ZeroDivisionError:
        if related_cheaters > 0:
            c_to_l = related_cheaters
        else:
            c_to_l = 0

    reports = len(list([x for x in player_data['history'] if x['type'] == 'report' and x['data']['reason'] == 'cheat' and x['data'].get('processedBy', None) is not None]))
    titled = int(player_data['assessment']['user'].get('title', None) is not None)
    followers = player_data['relation']['followers']
    blockers = player_data['relation']['blockers']

    try:
        b_to_f = blockers/float(followers)
    except ZeroDivisionError:
        if blockers > 0:
            b_to_f = blockers
        else:
            b_to_f = 0
    output = [int(status), ap.name, titled, reports, b_to_f, c_to_l] + ap.flags()
    print [int(status), ap.name, titled, reports, b_to_f, c_to_l] + ap.flags()
    writer.writerow(output)

def dump_csv_training_data(token):
    legits_pkl = get_files('test-data/saved/legits')
    cheaters_pkl = get_files('test-data/saved/cheaters')

    with open('test-data/player_data.csv', 'wb') as fh:
        writer = csv.writer(fh, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['cheating', 'name', 'titled', 'closed_reports', 'blocker_to_followers', 'cheaters_to_legits',
            'games_played', 'mb1', 'mb2', 'mb3', 'mb4', 'mb5', 'hb1', 'hb2', 'hb3', 'hb4', 'hb5', 'h1', 'h2', 'h3', 'h4', 'h5',
            'm1', 'm2', 'm3', 'm4', 'm5', 's1', 's2', 's3', 's4', 's5', 'r01', 'r02', 'r03', 'r04', 'r05',
            'r11', 'r12', 'r13', 'r14', 'r15', 'r51', 'r52', 'r53', 'r54', 'r55', 'r020p1', 'r020p2', 'r020p3', 'r020p4', 'r020p5',
            'r01220p1', 'r01220p2', 'r01220p3', 'r01220p4', 'r01220p5', 'cp201', 'cp202', 'cp203', 'cp204', 'cp205',
            'cp101', 'cp102', 'cp103', 'cp104', 'cp105', 'cp1001', 'cp1002', 'cp1003', 'cp1004', 'cp1005',
            'cpar11', 'cpar12', 'cpar13', 'cpar14', 'cpar15', 'cpar21', 'cpar22', 'cpar23', 'cpar24', 'cpar25'])
        for i in legits_pkl:
            try:
                with open('test-data/saved/legits/'+i, 'rb') as ap_f:
                    ap = pickle.load(ap_f)
                    add_row(writer, ap, False, token)
            except EOFError:
                pass
        for i in cheaters_pkl:
            try:
                with open('test-data/saved/cheaters/'+i, 'rb') as ap_f:
                    ap = pickle.load(ap_f)
                    add_row(writer, ap, True, token)
            except EOFError:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("token", metavar="TOKEN",
        help="secret token for the lichess api")
    settings = parser.parse_args()
    dump_csv_training_data(settings.token)