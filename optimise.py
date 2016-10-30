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

try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

# Build Network
n = FeedForwardNetwork()
inLayer = LinearLayer(61)
hidden_1 = SigmoidLayer(61)
hidden_2 = SigmoidLayer(20)
hidden_3 = SigmoidLayer(5)
outLayer = LinearLayer(1)

n.addInputModule(inLayer)
n.addModule(hidden_1)
n.addModule(hidden_2)
n.addModule(hidden_3)
n.addOutputModule(outLayer)

in_to_hidden_1 = FullConnection(inLayer, hidden_1)
hidden_1_to_hidden_2 = FullConnection(hidden_1, hidden_2)
hidden_2_to_hidden_3 = FullConnection(hidden_2, hidden_3)
hidden_3_to_out = FullConnection(hidden_3, outLayer)

n.addConnection(in_to_hidden_1)
n.addConnection(hidden_1_to_hidden_2)
n.addConnection(hidden_2_to_hidden_3)
n.addConnection(hidden_3_to_out)

n.sortModules()


ds = SupervisedDataSet(61, 1)

raw_flags = []
# Import Flags
with open('test-data/tensor_flags_dump.pkl', 'r') as input_pkl:
    raw_flags = pickle.load(input_pkl)
    for i in raw_flags:
        print i
        ds.addSample(i[0], i[1])

trainer = BackpropTrainer(n, ds)

cycles = 2000
for i in range(cycles):
    error = trainer.train()
    print str(i)+'/'+str(cycles)+': error '+str(error)

c_correct = 0
c_incorrect = 0
l_correct = 0
l_incorrect = 0

threshold = 0.68

for i, o in raw_flags:
    s = n.activate(i)
    if (o[0] == 0 and s[0] < threshold) or (o[0] == 1 and s[0] >= threshold):
        print bcolors.OKGREEN + 'Correct' + bcolors.ENDC
    else:
        print bcolors.WARNING + 'Incorrect' + bcolors.ENDC

    if o[0] == 0 and s[0] < threshold:
        l_correct += 1
    elif o[0] == 0 and s[0] >= threshold:
        l_incorrect += 1
    elif o[0] == 1 and s[0] >= threshold:
        c_correct += 1
    else:
        c_incorrect += 1

    print o
    print s

print 'Cheaters Correct: '+str(c_correct)
print 'Cheaters Incorrect: '+str(c_incorrect)
print 'Legits Correct: '+str(l_correct)
print 'Legits incorrect: '+str(l_incorrect)

with open('neuralnet.pkl', 'w+') as output:
    pickle.dump(n, output)