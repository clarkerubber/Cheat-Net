import chess
import chess.uci
import chess.pgn
import logging
import modules.analysis

from modules.analysis.tools import avg
from modules.bcolors.bcolors import bcolors
from operator import methodcaller

class AnalysedPlayer:
    def __init__(self, name, games, gamesPlayed, cheater, related):
        self.name = name    # str
        self.games = games  # list(AnalysableGame)
        self.gamesPlayed = gamesPlayed # # of games played
        self.cheater = cheater # True, False, None
        self.related = related # list(userId)

    def assess(self):
        flags = []
        flags.append(self.accuracy_given_advantage(advantage = 150, threshold = 10) >= 91.0)
        flags.append(self.accuracy_given_scaled_advantage(advantage = 150, threshold = 10) >= 91.0)
        flags.append(self.accuracy_given_advantage(advantage = 200, threshold = 30) >= 93.5)
        flags.append(self.accuracy_given_scaled_advantage(advantage = 200, threshold = 30) >= 93.5)
        flags.append(self.assess_rank_0_percents())
        flags.append(self.assess_rank_01_percents())
        flags.append(self.assess_rank_5less_percents())
        flags.append(self.assess_rank_0_move20plus_percents())
        return (sum(flags) > 0)

    # Assessment Tools
    def weights_mask(self, weights, mb, hb, ho, mt):
        mod = [0]
        if mb:
            mod.append(weights.get('mb', 0))
        if hb:
            mod.append(weights.get('hb', 0))
        if ho:
            mod.append(weights.get('ho', 0))
        if mt:
            mod.append(weights.get('mt', 0))
        if mb and mt:
            mod.append(weights.get('mbmt', 0))
        if hb and mt:
            mod.append(weights.get('hbmt', 0))
        if ho and mt:
            mod.append(weights.get('homt', 0))
        return max(mod)

    def assess_rank_0_percents(self, averg = 61.0, maxim = 77.0, weights = {'mb': 8, 'homt': 99, 'mt': 10, 'ho': 24, 'mbmt': 99, 'hb': 12, 'hbmt': 99}):
        flags = []
        flags.append(avg(self.rank_0_percents()) >= averg)
        for r, mb, hb, ho, mt in zip(self.rank_0_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            flags.append(r >= (maxim - self.weights_mask(weights, mb, hb, ho, mt)))
        return (sum(flags) > 0)

    def assess_rank_01_percents(self, averg = 69.0, maxim = 95.0, weights = {'mb': 0, 'homt': 99, 'mt': 11, 'ho': 33, 'mbmt': 99, 'hb': 0, 'hbmt': 99}):
        flags = []
        flags.append(avg(self.rank_01_percents()) >= averg)
        for r, mb, hb, ho, mt in zip(self.rank_01_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            flags.append(r >= (maxim - self.weights_mask(weights, mb, hb, ho, mt)))
        return (sum(flags) > 0)

    def assess_rank_5less_percents(self, averg = 101.0, maxim = 101.0, weights = {'mb': 8, 'homt': 99, 'mt': 4, 'ho': 22, 'mbmt': 99, 'hb': 8, 'hbmt': 99}):
        flags = []
        flags.append(avg(self.rank_5less_percents()) >= averg)
        for r, mb, hb, ho, mt in zip(self.rank_5less_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            flags.append(r >= (maxim - self.weights_mask(weights, mb, hb, ho, mt)))
        return (sum(flags) > 0)

    def assess_rank_0_move20plus_percents(self, averg = 27.0, maxim = 77.0, weights = {'mb': 0, 'homt': 99, 'mt': 32, 'ho': 76, 'mbmt': 99, 'hb': 0, 'hbmt': 99}):
        flags = []
        flags.append(avg(self.rank_0_move20plus_percents()) >= averg)
        for r, mb, hb, ho, mt in zip(self.rank_0_move20plus_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            flags.append(r >= (maxim - self.weights_mask(weights, mb, hb, ho, mt)))
        return (sum(flags) > 0)

    def assess_cpl20_percents(self, averg = 85.0, maxim = 97.0, weights = {'mb': 14, 'homt': 99, 'mt': 4, 'ho': 24, 'mbmt': 99, 'hb': 14, 'hbmt': 99}):
        flags = []
        flags.append(avg(self.cpl20_percents()) >= averg)
        for r, mb, hb, ho, mt in zip(self.cpl20_percents(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
            flags.append(r >= (maxim - self.weights_mask(weights, mb, hb, ho, mt)))
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

    def rank_5less_percents(self):
        return list(i.analysed.rank_5less_percent() for i in self.games)

    def cpl20_percents(self):
        return list(i.analysed.cpl20_percent() for i in self.games)

    def accuracy_percentages(self, cp):
        return list(i.analysed.accuracy_percentage(cp) for i in self.games)

    def scaled_accuracy_percentages(self, bound):
        return list(i.analysed.scaled_accuracy_percentage(bound) for i in self.games)

    def accuracy_percentages_20(self, cp):
        return list(i.analysed.accuracy_percentage_20(cp) for i in self.games)

    def accuracy_given_advantage(self, advantage, threshold):
        a = list(i.analysed.accuracy_given_advantage(advantage, threshold) for i in self.games)
        accurate_moves = sum(list(i[0] for i in a))
        disadvantaged_positions = sum(list(i[1] for i in a))
        if disadvantaged_positions > 10:
            return 100*accurate_moves/float(disadvantaged_positions)
        else:
            return 0

    def accuracy_given_scaled_advantage(self, scaled_advantage, scaled_threshold):
        a = list(i.analysed.accuracy_given_scaled_advantage(scaled_advantage, scaled_threshold) for i in self.games)
        accurate_moves = sum(list(i[0] for i in a))
        disadvantaged_positions = sum(list(i[1] for i in a))
        if disadvantaged_positions > 10:
            return 100*accurate_moves/float(disadvantaged_positions)
        else:
            return 0
