import logging
import chess.pgn
import matplotlib.pyplot as plt
import numpy as np
from modules.analysis.tools import avg, bounded_eval
from modules.bcolors.bcolors import bcolors

class AnalysedGame: # subjective to the player being analysed
    def __init__(self, assessment, positions):
        self.assessment = assessment # PlayerAssessment
        self.positions = positions  # list(AnalysedPosition)

    def move_numbers(self):
        return list(range(len(self.positions)))

    def graph_all(self):
        self.graph_rank_v_sd()
        self.graph_error_v_sd()
        self.graph_rank_v_percent()

    def graph_rank_v_sd(self):
        x = self.top_five_sds()
        y = self.ranks()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('top 5 std')
        ax.set_ylabel('move rank')
        fig.show()

    def graph_error_v_sd(self):
        x = self.top_five_sds()
        y = self.actual_errors()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('top 5 std')
        ax.set_ylabel('move error')
        fig.show()

    def graph_rank_v_percent(self):
        x = self.percent_errors()
        y = self.ranks()

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_xlabel('percent error')
        ax.set_ylabel('move rank')
        fig.show()

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

    def rank_5more_percent(self):
        start = 20
        try:
            if len(self.positions[start:]) > 10:
                return 100*sum((i.rank() > 5) for i in self.positions[start:])/float(len(self.positions[start:]))
            else:
                return 100
        except ValueError:
            return 100

    def error_difs(self):
        return list(i.error_dif() for i in self.positions)

    def avg_error_dif(self):
        return avg(self.error_difs())

    def top_five_sds(self):
        return list(i.top_five_sd() for i in self.positions)

    def expected_errors(self):
        return list(i.expected_error() for i in self.positions)

    def ranks(self):
        return list(i.rank() for i in self.positions)

    def avg_rank(self):
        return avg(self.ranks())

    def actual_errors(self):
        return list(i.actual_error() for i in self.positions)

    def avg_error(self):
        return avg(self.errors())

    def percent_errors(self):
        return list(i.percent_error() for i in self.positions)

    def accuracy_percentage(self, cp):
        if len(self.positions) > 0:
            return 100*sum(i.accuracy_less_than(cp) for i in self.positions)/float(len(self.positions))
        else:
            return 0

    def tactics_seized(self, loss, gain):
        last_best = 0
        total_tactics = 0
        seized_tactics = 0
        for best, played, position in zip(list(i.best_eval for i in self.positions), list(bounded_eval(i.played.sort_val) for i in self.positions), self.positions):
            if last_best - best > loss:
                total_tactics += 1
                if position.actual_error() < gain:
                    seized_tactics += 1
        return (seized_tactics, total_tactics)

    def accuracy_percentage_20(self, cp):
        start = 15
        end = 30
        try:
            if len(self.positions[start:]) > 10:
                return 100*sum(i.accuracy_less_than(cp) for i in self.positions[start:])/float(len(self.positions[start:]))
            else:
                return 0
        except ValueError:
            return 0