import logging
import chess.pgn
from modules.analysis.tools import avg, bounded_eval, scaled_eval
from modules.bcolors.bcolors import bcolors

class AnalysedGame: # subjective to the player being analysed
    def __init__(self, assessment, positions):
        self.assessment = assessment # PlayerAssessment
        self.positions = positions  # list(AnalysedPosition)

    def move_numbers(self):
        return list(range(len(self.positions)))

    def length(self):
        return len(self.positions)

    def rank_0_percent(self):
        if len(self.positions) > 10:
            return 100*sum(i.rank() == 0 for i in self.positions)/float(self.length())
        else:
            return 0

    def rank_1_percent(self):
        if self.length() > 10:
            return 100*sum(i.rank() == 1 for i in self.positions)/float(self.length())
        else:
            return 0

    def rank_01_percent(self):
        start = 0
        if len(self.positions[start:]) > 10:
            return 100*sum(i.rank() < 2 for i in self.positions[start:])/float(len(self.positions[start:]))
        else:
            return 0

    def rank_0_move20plus_percent(self):
        if len(self.positions[20:]) > 15:
            return 100*sum(i.rank() == 0 for i in self.positions[20:])/float(len(self.positions[20:]))
        else:
            return 0

    def rank_012_move20plus_percent(self):
        if len(self.positions[20:]) > 15:
            return 100*sum(i.rank() < 3 for i in self.positions[20:])/float(len(self.positions[20:]))
        else:
            return 0

    def rank_5more_percent(self):
        if len(self.positions) > 10:
            return 100*sum(i.rank() > 4 for i in self.positions)/float(self.length())
        else:
            return 0

    def cpl_percent(self, cp):
        if self.length() > 10:
            return 100*sum(i.actual_error() < cp for i in self.positions)/float(self.length())
        else:
            return 0

    def cpl_greater_percent(self, cp):
        if self.length() > 10:
            return 100*sum(i.actual_error() > cp for i in self.positions)/float(self.length())
        else:
            return 0

    def error_difs(self):
        return list(i.error_dif() for i in self.positions)

    def scaled_error_difs(self):
        return list(i.scaled_error_dif() for i in self.positions)

    def avg_error_dif(self):
        return avg(self.error_difs())

    def avg_scaled_error_dif(self):
        return avg(self.scaled_error_difs())

    def top_five_sds(self):
        return list(i.top_five_sd() for i in self.positions)

    def top_five_scaled_sds(self):
        return list(i.top_five_scaled_sd() for i in self.positions)

    def avg_rank(self):
        return avg(self.ranks())

    def actual_errors(self):
        return list(i.actual_error() for i in self.positions)

    def actual_scaled_errors(self):
        return list(i.actual_error() for i in self.positions)

    def avg_error(self):
        return avg(self.errors())

    def accuracy_percentage(self, cp):
        if self.length() > 0:
            return 100*sum(i.accuracy_less_than(cp) for i in self.positions)/float(self.length())
        else:
            return 0

    def avg_cpl_given_rank(self, rank):
        return avg(list(i.actual_error() for i in self.positions if i.rank() <= rank and i.rank != 0))
