import chess
import chess.uci
import chess.pgn
import logging
import modules.analysis

from modules.analysis.tools import avg, weights_mask, weighted_avg
from modules.bcolors.bcolors import bcolors
from operator import methodcaller
from modules.analysis.tensorflow.tf_trainer_1game import apply_net

class AnalysedPlayer:
    def __init__(self, name, games, gamesPlayed, cheater, related_legits, related_cheaters, titled, blockers, followers, reports):
        self.name = name    # str
        self.games = games  # list(AnalysableGame)
        self.gamesPlayed = gamesPlayed # # of games played
        self.cheater = cheater # True, False, None
        self.related_legits = len(related_legits)
        self.related_cheaters = len(related_cheaters)
        self.titled = int(titled)
        self.blockers = blockers # int
        self.followers = followers # int
        self.reports = reports # int
        try:
            self.c_to_l = self.related_cheaters/float(self.related_legits)
        except ZeroDivisionError:
            if self.related_cheaters > 0:
                self.c_to_l = self.related_cheaters
            else:
                self.c_to_l = 0
        try:
            self.b_to_f = self.blockers/float(self.followers)
        except ZeroDivisionError:
            if self.blockers > 0:
                self.b_to_f = self.blockers
            else:
                self.b_to_f = 0

    def flags(self):
        flags = []
        if len(self.games) > 2:
            flags.extend(self.mblurs())
            flags.extend(self.hblurs())
            flags.extend(self.holds())
            flags.extend(self.move_times())
            flags.extend(self.sf_average())
            flags.extend(self.rank_0_percents())
            flags.extend(self.rank_1_percents())
            flags.extend(self.rank_5more_percents())
            flags.extend(self.rank_0_move20plus_percents())
            flags.extend(self.rank_012_move20plus_percents())
            flags.extend(self.cpl_percents(20))
            flags.extend(self.cpl_percents(10))
            flags.extend(self.cpl_greater_percents(100))
            flags.extend(self.avg_cpl_given_rank(1))
            flags.extend(self.avg_cpl_given_rank(2))
            gamified = [list([i for x, i in enumerate(flags) if x%len(self.games) == y]) for y in range(len(self.games))]
            for x, g in enumerate(gamified):
                gamified[x] = [self.titled, self.reports, self.b_to_f, self.c_to_l, self.gamesPlayed] + g
            return gamified
        return []

    def assess_and_report(self):
        return (self.assess(), self.report())

    def assess(self):
        if self.activation() > 1:
            return True
        return False

    def report(self):
        if len(self.flags()) > 0:
            output = str(self.activation())+'/'+str(len(self.games))+' games cheating, '+str(round(avg(self.rank_01_percents()), 1))+"% Rank 1 PV\n"
            output += "\n".join([('https://lichess.org/' + g.assessment.id + " " + str(round(100*a[1], 1)) + '%') for g, a in zip(self.games, self.activations())])
            return output
        else:
            return 'not enough games to create assessment'

    def activations(self):
        flags = self.flags()
        return apply_net(flags)[0]

    def activation(self):
        flags = self.flags()
        if len(flags) > 0:
            return sum(g[1] > 0.6 for g in apply_net(flags)[0])
        return 0

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

    def avg_cpl_given_rank(self, rank):
        return list(i.analysed.avg_cpl_given_rank(rank) for i in self.games)

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