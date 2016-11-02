#!/usr/bin/env python

"""Optimise neural net"""

import argparse
import logging
import os
import pickle
from modules.bcolors.bcolors import bcolors
from pybrain.structure import FeedForwardNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet

# Build Network
def optimise():
    n = FeedForwardNetwork()
    inLayer = LinearLayer(91)
    hidden_1 = SigmoidLayer(91)
    hidden_2 = SigmoidLayer(50)
    hidden_3 = SigmoidLayer(20)
    hidden_4 = SigmoidLayer(10)
    hidden_5 = SigmoidLayer(5)
    hidden_6 = SigmoidLayer(5)
    outLayer = LinearLayer(1)

    n.addInputModule(inLayer)
    n.addModule(hidden_1)
    n.addModule(hidden_2)
    n.addModule(hidden_3)
    n.addModule(hidden_4)
    n.addModule(hidden_5)
    n.addModule(hidden_6)
    n.addOutputModule(outLayer)

    in_to_hidden_1 = FullConnection(inLayer, hidden_1)
    hidden_1_to_hidden_2 = FullConnection(hidden_1, hidden_2)
    hidden_2_to_hidden_3 = FullConnection(hidden_2, hidden_3)
    hidden_3_to_hidden_4 = FullConnection(hidden_3, hidden_4)
    hidden_4_to_hidden_5 = FullConnection(hidden_4, hidden_5)
    hidden_5_to_hidden_6 = FullConnection(hidden_5, hidden_6)
    hidden_6_to_out = FullConnection(hidden_6, outLayer)

    n.addConnection(in_to_hidden_1)
    n.addConnection(hidden_1_to_hidden_2)
    n.addConnection(hidden_2_to_hidden_3)
    n.addConnection(hidden_3_to_hidden_4)
    n.addConnection(hidden_4_to_hidden_5)
    n.addConnection(hidden_5_to_hidden_6)
    n.addConnection(hidden_6_to_out)

    n.sortModules()


    ds = SupervisedDataSet(91, 1)

    raw_flags = []
    # Import Flags
    with open('test-data/tensor_flags_dump.pkl', 'r') as input_pkl:
        raw_flags = pickle.load(input_pkl)
        for i in raw_flags:
            ds.addSample(i[0], i[1])

    trainer = BackpropTrainer(n, ds)

    cycles = 2000
    for i in range(cycles):
        error = trainer.train()

    c_correct = 0
    c_incorrect = 0
    l_correct = 0
    l_incorrect = 0

    threshold = 0.7

    for i, o in raw_flags:
        s = n.activate(i)
        if o[0] == 0 and s[0] < threshold:
            l_correct += 1
        elif o[0] == 0 and s[0] >= threshold:
            l_incorrect += 1
        elif o[0] == 1 and s[0] >= threshold:
            c_correct += 1
        else:
            c_incorrect += 1

    print 'Cheaters Correct: '+str(c_correct)
    print 'Cheaters Incorrect: '+str(c_incorrect)
    print 'Legits Correct: '+str(l_correct)
    print 'Legits incorrect: '+str(l_incorrect)

    with open('neuralnet.pkl', 'w+') as output:
        pickle.dump(n, output)

#optimise()