import chess
import chess.uci
import chess.pgn
import logging
import modules.analysis

from modules.analysis.tools import avg, weights_mask, weighted_avg
from modules.bcolors.bcolors import bcolors
from operator import methodcaller

class AnalysedPlayer:
    def __init__(self, name, games, gamesPlayed, cheater, related):
        self.name = name    # str
        self.games = games  # list(AnalysableGame)
        self.gamesPlayed = gamesPlayed # # of games played
        self.cheater = cheater # True, False, None
        self.related = related # list(userId)

    def flags(self):
        flags = []
        if len(self.games) > 0:
            self.games = self.games + (5 - len(self.games)) * [self.games[-1]]
            flags.append(self.gamesPlayed)
            flags.extend(self.mblurs())
            flags.extend(self.hblurs())
            flags.extend(self.holds())
            flags.extend(self.move_times())
            flags.extend(self.move_times_average())
            flags.extend(self.move_times_sd())
            flags.extend(self.sf_average())
            flags.extend(self.game_lengths())
            flags.extend(self.rank_0_percents())
            flags.extend(self.rank_1_percents())
            flags.extend(self.rank_5more_percents())
            flags.extend(self.rank_0_move20plus_percents())
            flags.extend(self.rank_012_move20plus_percents())
            flags.extend(self.cpl_percents(20))
            flags.extend(self.cpl_percents(10))
            flags.extend(self.cpl_greater_percents(100))
        return flags

    def assess_and_report(self, net):
        return (self.assess(net), self.report(net))

    def assess(self, net):
        if self.activation(net) > 0.7:
            return True
        return False

    def report(self, net):
        if len(self.flags()) > 0:
            output = str(round(100*self.activation(net), 1))+'% confidence of cheating, '+str(round(avg(self.rank_01_percents()), 1))+'% Rank 1 PV'
            return output
        else:
            return 'not enough games to create assessment'

    def activation(self, net):
        flags = self.flags()
        if len(flags) > 0:
            return net.activate(tuple(flags))[0]
        return 0.0

    # Data Collectors
        # Assessment
    def mblurs(self):
        return list(int(i.analysed.assessment.flags.mbr) for i in self.games)

    def hblurs(self):
        return list(int(i.analysed.assessment.flags.hbr) for i in self.games)

    def holds(self):
        return list(int(i.analysed.assessment.hold) for i in self.games)

    def move_times(self):
        return list(int(i.analysed.assessment.flags.cmt) for i in self.games)

    def move_times_average(self):
        return list(int(i.analysed.assessment.mtAvg) for i in self.games)

    def move_times_sd(self):
        return list(int(i.analysed.assessment.mtSd) for i in self.games)

    def sf_average(self):
        return list(int(i.analysed.assessment.sfAvg) for i in self.games)

        # Game
    def ranks(self):
        return sum(list(i.analysed.ranks() for i in self.games), [])

    def game_lengths(self):
        return list(i.analysed.length() for i in self.games)

    def rank_0_percents(self):
        return list(i.analysed.rank_0_percent() for i in self.games)

    def rank_1_percents(self):
        return list(i.analysed.rank_1_percent() for i in self.games)

    def rank_01_percents(self):
        return list(i.analysed.rank_01_percent() for i in self.games)

    def rank_0_move20plus_percents(self):
        return list(i.analysed.rank_0_move20plus_percent() for i in self.games)

    def rank_012_move20plus_percents(self):
        return list(i.analysed.rank_012_move20plus_percent() for i in self.games)

    def rank_5more_percents(self):
        return list(i.analysed.rank_5more_percent() for i in self.games)

    def cpl_percents(self, cp):
        return list(i.analysed.cpl_percent(cp) for i in self.games)

    def cpl_greater_percents(self, cp):
        return list(i.analysed.cpl_greater_percent(cp) for i in self.games)

    def accuracy_percentages(self, cp):
        return list(i.analysed.accuracy_percentage(cp) for i in self.games)

    def scaled_accuracy_percentages(self, bound):
        return list(i.analysed.scaled_accuracy_percentage(bound) for i in self.games)

    def accuracy_percentages_20(self, cp):
        return list(i.analysed.accuracy_percentage_20(cp) for i in self.games)

    def tactics_seized(self, minadv, maxadv, threshold):
        return list(i.analysed.tactics_seized(minadv, maxadv, threshold) for i in self.games)