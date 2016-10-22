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

    def rank_0_percent(self):
        if len(self.positions) > 10:
            return 100*sum(i.rank() == 0 for i in self.positions)/float(len(self.positions))
        else:
            return 0

    def rank_01_percent(self):
        start = 20
        if len(self.positions[start:]) > 10:
            return 100*sum(i.rank() < 2 for i in self.positions[start:])/float(len(self.positions[start:]))
        else:
            return 0

    def rank_0_move20plus_percent(self):
        if len(self.positions[20:]) > 20:
            return 100*sum(i.rank() == 0 for i in self.positions[20:])/float(len(self.positions[20:]))
        else:
            return 0

    def rank_5less_percent(self):
        start = 0
        if len(self.positions[start:]) > 10:
            return 100*sum(i.rank() < 4 for i in self.positions[start:])/float(len(self.positions[start:]))
        else:
            return 0

    def cpl20_percent(self):
        start = 0
        if len(self.positions[start:]) > 10:
            return 100*sum(i.actual_error() < 20 for i in self.positions[start:])/float(len(self.positions[start:]))
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
        if len(self.positions) > 0:
            return 100*sum(i.accuracy_less_than(cp) for i in self.positions)/float(len(self.positions))
        else:
            return 0

    def accuracy_given_advantage(self, advantage, threshold):
        total_tactics = 0
        seized_tactics = 0
        for best, played, position in zip(list(i.best_eval for i in self.positions), list(bounded_eval(i.played.sort_val()) for i in self.positions), self.positions):
            if (-best) > advantage:
                total_tactics += 1
                if position.actual_error() < threshold:
                    seized_tactics += 1
        return (seized_tactics, total_tactics)

    def accuracy_given_scaled_advantage(self, scaled_advantage, scaled_threshold):
        total_tactics = 0
        seized_tactics = 0
        for best, played, position in zip(list(i.best_scaled_eval for i in self.positions), list(bounded_eval(scaled_eval(i.played.sort_val())) for i in self.positions), self.positions):
            if (-best) > scaled_advantage:
                total_tactics += 1
                if position.actual_scaled_error() < scaled_threshold:
                    seized_tactics += 1
        return (seized_tactics, total_tactics)
