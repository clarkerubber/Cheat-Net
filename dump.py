#!/usr/bin/env python

"""Analysing players for lichess.org"""

import sys
import pickle
from modules.api.tools import get_files

sys.setrecursionlimit(2000)

def dump_dir(dr, engine):
    in_pkl = get_files(dr)
    out = []
    for i in in_pkl:
        with open(dr+i, 'rb') as inputpkl:
            d = pickle.load(inputpkl)
            if len(d.flags()) > 1:
                out.append((tuple(d.flags()), (int(engine),)))
    return out

def dump_training_data():
    dump = dump_dir('test-data/saved/legits/', 0) + dump_dir('test-data/saved/cheaters/', 1)

    with open('test-data/tensor_flags_dump.pkl', 'w+') as output:
        pickle.dump(dump, output, pickle.HIGHEST_PROTOCOL)

#dump_training_data()