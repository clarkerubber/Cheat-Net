# Cheat-Net

## About

This is a python application dedicated to analysing reported cheaters on lichess.

## Installation

This script requires the *Requests*, *Python-Chess*, *PyBrain*, *SciPy* and *NumPy* libraries to run, as well as a copy of *Stockfish*

### Install Requests

`pip install requests`

### Install Python Chess

`pip install python-chess`

### Install SciPy

`pip install scipy`

### Install NumPy

`pip install numpy`

### Install PyBrain

`git clone https://github.com/pybrain/pybrain.git`
`cd pybrain`
`python setup.py install`

### Setup

MacOS / Linux : `sh build-stockfish.sh` to obtain the current lichess Stockfish instance.

## Launching Application

`python main.py <Secret API Token> <#Threads = 4> <Hash (Bytes) = 2048>`

If your system has systemd, you can use the service file provided, it is tuned for a local virtualenv in a dedicated user account. If you run it as root with system-wide pip packages, use `ExecStart=/usr/bin/python main.py --quiet $key $instance $threads`

