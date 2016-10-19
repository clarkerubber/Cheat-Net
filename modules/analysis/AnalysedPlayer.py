import chess
import chess.uci
import chess.pgn
import logging
import modules.analysis

from modules.analysis.tools import avg
from modules.bcolors.bcolors import bcolors
from operator import methodcaller

import matplotlib.pyplot as plt
import numpy as np

class AnalysedPlayer:
    def __init__(self, name, games, gamesPlayed, cheater, related):
        self.name = name    # str
        self.games = games  # list(AnalysableGame)
        self.gamesPlayed = gamesPlayed # # of games played
        self.cheater = cheater # True, False, None
        self.related = related # list(userId)

    def assess(self):
        flags = []
        flags.append(self.tactics_seized(150, 10)    >= 91.0)
        flags.append(self.tactics_seized(200, 30)    >= 93.5)
        flags.append(avg(self.rank_5more_percents(), default = 100) <= 19.5)
        flags.append(self.assess_rank_0_percents())
        flags.append(self.assess_rank_01_percents())
        flags.append(self.assess_rank_0_move20plus_percents())
        return (sum(flags) > 0)

    # Assessment Tools

    def assess_rank_0_percents(self):
        flags = []
        flags.append(avg(self.rank_0_percents()) >= 61.0)
        for r, mb, hb, ho, mt in zip(self.rank_0_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            if hb or ho:
                mod = 7
            elif mt:
                mod = 6
            elif mb:
                mod = 4
            else:
                mod = 0
            try:
                flags.append(r >= (73.0 - mod))
            except ValueError:
                pass

        return (sum(flags) > 0)

    def assess_rank_01_percents(self):
        flags = []
        flags.append(avg(self.rank_01_percents()) >= 69.0)
        for r, mb, hb, ho, mt in zip(self.rank_01_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            if ho or mt:
                mod = 11
            elif mb or hb:
                mod = 0
            else:
                mod = 0
            try:
                flags.append(r >= (95.0 - mod))
            except ValueError:
                pass

        return (sum(flags) > 0)

    def assess_rank_0_move20plus_percents(self):
        flags = []
        flags.append(avg(self.rank_0_move20plus_percents()) >= 27.0)
        for r, mb, hb, ho, mt in zip(self.rank_0_move20plus_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            if ho or mt:
                mod = 30
            elif mb or hb:
                mod = 0
            else:
                mod = 0
            try:
                flags.append(r >= (77.0 - mod))
            except ValueError:
                pass

        return (sum(flags) > 0)

    # Data Collectors
        # Assessment
    def mblurs(self):
        return list(i.analysed.assessment.flags.mbr for i in self.games)

    def hblurs(self):
        return list(i.analysed.assessment.flags.hbr for i in self.games)

    def holds(self):
        return list(i.analysed.assessment.hold for i in self.games)

    def move_times(self):
        return list(i.analysed.assessment.flags.cmt for i in self.games)

        # Game
    def ranks(self):
        return sum(list(i.analysed.ranks() for i in self.games), [])

    def rank_0_percents(self):
        return list(i.analysed.rank_0_percent() for i in self.games)

    def rank_01_percents(self):
        return list(i.analysed.rank_01_percent() for i in self.games)

    def rank_0_move20plus_percents(self):
        return list(i.analysed.rank_0_move20plus_percent() for i in self.games)

    def rank_5more_percents(self):
        return list(i.analysed.rank_5more_percent() for i in self.games)

    def accuracy_percentages(self, cp):
        return list(i.analysed.accuracy_percentage(cp) for i in self.games)

    def accuracy_percentages_20(self, cp):
        return list(i.analysed.accuracy_percentage_20(cp) for i in self.games)

    def tactics_seized(self, loss, gain):
        a = list(i.analysed.tactics_seized(loss, gain) for i in self.games)
        tactics_seized = sum(list(i[0] for i in a))
        total_tactics = sum(list(i[1] for i in a))
        if total_tactics > 10:
            return 100*tactics_seized/float(total_tactics)
        else:
            return 0