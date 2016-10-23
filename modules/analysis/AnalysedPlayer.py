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
        if len(games) < 3:
            return False
        flags = []
        flags.append(self.accuracy_given_advantage(advantage = 150, threshold = 10) >= 92.0)
        flags.append(self.accuracy_given_scaled_advantage(scaled_advantage = 150, scaled_threshold = 10) >= 94.0)
        flags.append(self.accuracy_given_advantage(advantage = 200, threshold = 30) >= 94.5)
        flags.append(self.accuracy_given_scaled_advantage(scaled_advantage = 200, scaled_threshold = 30) >= 94.0)

        flags.append(self.assess_rank_0_percents(
            averg = 58,
            maxim = 73,
            weights = {'mb': 0, 'homt': 99, 'mt': 1, 'ho': 99, 'mbmt': 99, 'hb': 21, 'hbmt': 99}
        ))

        flags.append(self.assess_rank_1_percents(
            averg = 25,
            maxim = 39,
            weights = {'mb': 15, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 15, 'hbmt': 99}
        ))

        flags.append(self.assess_rank_01_percents(
            averg = 62,
            maxim = 93,
            weights = {'mb': 14, 'homt': 99, 'mt': 9, 'ho': 99, 'mbmt': 99, 'hb': 14, 'hbmt': 99}
        ))

        flags.append(self.assess_rank_5less_percents(
            averg = 101,
            maxim = 101,
            weights = {'mb': 8, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 8, 'hbmt': 99}
        ))

        flags.append(self.assess_rank_0_move20plus_percents(
            averg = 27,
            maxim = 77,
            weights = {'mb': 35, 'homt': 99, 'mt': 76, 'ho': 99, 'mbmt': 99, 'hb': 35, 'hbmt': 99}
        ))

        flags.append(self.assess_cpl20_percents(
            averg = 101,
            maxim = 101,
            weights = {'mb': 20, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 21, 'hbmt': 99}
        ))

        flags.append(self.assess_cpl10_percents(
            averg = 79,
            maxim = 91,
            weights = {'mb': 14, 'homt': 99, 'mt': 5, 'ho': 99, 'mbmt': 99, 'hb': 14, 'hbmt': 99}
        ))
        return (sum(flags) > 0)

    # Assessors
    def assess_rank_0_percents(self, averg, maxim, weights):
        return self.assess_func(self.rank_0_percents, averg, maxim, weights)

    def assess_rank_1_percents(self, averg, maxim, weights):
        return self.assess_func(self.rank_1_percents, averg, maxim, weights)

    def assess_rank_01_percents(self, averg, maxim, weights):
        return self.assess_func(self.rank_01_percents, averg, maxim, weights)

    def assess_rank_5less_percents(self, averg, maxim, weights):
        return self.assess_func(self.rank_5less_percents, averg, maxim, weights)

    def assess_rank_0_move20plus_percents(self, averg, maxim, weights):
        return self.assess_func(self.rank_0_move20plus_percents, averg, maxim, weights)

    def assess_cpl20_percents(self, averg, maxim, weights):
        return self.assess_func(self.cpl20_percents, averg, maxim, weights)

    def assess_cpl10_percents(self, averg, maxim, weights):
        return self.assess_func(self.cpl10_percents, averg, maxim, weights)

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

    def assess_func(self, func, averg, maxim, weights):
        flags = []
        if len(self.games) > 2:
            flags.append(avg(func()) >= averg)
        for r, mb, hb, ho, mt in zip(func(), self.mblurs(), self.hblurs(), self.holds(), self.move_times()):
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

    def rank_1_percents(self):
        return list(i.analysed.rank_1_percent() for i in self.games)

    def rank_01_percents(self):
        return list(i.analysed.rank_01_percent() for i in self.games)

    def rank_0_move20plus_percents(self):
        return list(i.analysed.rank_0_move20plus_percent() for i in self.games)

    def rank_5less_percents(self):
        return list(i.analysed.rank_5less_percent() for i in self.games)

    def cpl20_percents(self):
        return list(i.analysed.cpl20_percent() for i in self.games)

    def cpl10_percents(self):
        return list(i.analysed.cpl10_percent() for i in self.games)

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
