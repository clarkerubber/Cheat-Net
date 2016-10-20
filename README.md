# Cheat-Net

## About

This is a python application dedicated to analysing reported cheaters on lichess.

## Installation

This script requires the *Requests* and *Python-Chess* libraries to run, as well as a copy of *Stockfish*

### Install Requests

`pip install requests`

### Install Python Chess

`pip install python-chess`

### Setup

MacOS / Linux : `sh build-stockfish.sh` to obtain the current lichess Stockfish instance.

## Launching Application

`python main.py <Secret API Token> <#Threads = 4> <Hash (Bytes) = 2048>`

If your system has systemd, you can use the service file provided, it is tuned for a local virtualenv in a dedicated user account. If you run it as root with system-wide pip packages, use `ExecStart=/usr/bin/python main.py --quiet $key $instance $threads`

