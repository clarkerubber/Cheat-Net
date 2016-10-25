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

    def assess(self):
        flags = []
        
        flags.extend(self.assess_rank_0_percents(
            averg = 69,
            maxim = 74,
            weights = {'mb': 0, 'homt': 99, 'mt': 2, 'ho': 99, 'mbmt': 99, 'hb': 4, 'hbmt': 99},
            avgweights = {'mb': 0, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 0, 'hbmt': 99}
        ))
        flags.extend(self.assess_rank_1_percents(
            averg = 29,
            maxim = 42,
            weights = {'mb': 18, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 18, 'hbmt': 99},
            avgweights = {'mb': 8, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 8, 'hbmt': 99}
        ))
        flags.extend(self.assess_rank_01_percents(
            averg = 62,
            maxim = 93,
            weights = {'mb': 2, 'homt': 99, 'mt': 9, 'ho': 99, 'mbmt': 99, 'hb': 14, 'hbmt': 99},
            avgweights = {'mb': 5, 'homt': 99, 'mt': 10, 'ho': 99, 'mbmt': 99, 'hb': 5, 'hbmt': 99}
        ))
        flags.extend(self.assess_rank_5less_percents(
            averg = 93,
            maxim = 100,
            weights = {'mb': 2, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 7, 'hbmt': 99},
            avgweights = {'mb': 0, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 2, 'hbmt': 99}
        ))
        flags.extend(self.assess_rank_0_move20plus_percents(
            averg = 27,
            maxim = 77,
            weights = {'mb': 11, 'homt': 99, 'mt': 40, 'ho': 99, 'mbmt': 99, 'hb': 35, 'hbmt': 99},
            avgweights = {'mb': 13, 'homt': 99, 'mt': 12, 'ho': 99, 'mbmt': 99, 'hb': 17, 'hbmt': 99}
        ))
        flags.extend(self.assess_cpl20_percents(
            averg = 88,
            maxim = 100,
            weights = {'mb': 13, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 13, 'hbmt': 99},
            avgweights = {'mb': 2, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 3, 'hbmt': 99}
        ))
        flags.extend(self.assess_cpl10_percents(
            averg = 85,
            maxim = 97,
            weights = {'mb': 10, 'homt': 99, 'mt': 11, 'ho': 99, 'mbmt': 99, 'hb': 14, 'hbmt': 99},
            avgweights = {'mb': 4, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 5, 'hbmt': 99}
        ))
        flags.extend(self.assess_cpl5_percents(
            averg = 80,
            maxim = 97,
            weights = {'mb': 14, 'homt': 99, 'mt': 15, 'ho': 99, 'mbmt': 99, 'hb': 14, 'hbmt': 99},
            avgweights = {'mb': 3, 'homt': 99, 'mt': 0, 'ho': 99, 'mbmt': 99, 'hb': 4, 'hbmt': 99}
        ))

        return max(flags or [0]) > 0

    # Assessors
    def assess_rank_0_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.rank_0_percents(), averg, maxim, weights, avgweights)

    def assess_rank_1_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.rank_1_percents(), averg, maxim, weights, avgweights)

    def assess_rank_01_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.rank_01_percents(), averg, maxim, weights, avgweights)

    def assess_rank_5less_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.rank_5less_percents(), averg, maxim, weights, avgweights)

    def assess_rank_0_move20plus_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.rank_0_move20plus_percents(), averg, maxim, weights, avgweights)

    def assess_cpl20_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.cpl_percents(20), averg, maxim, weights, avgweights)

    def assess_cpl10_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.cpl_percents(10), averg, maxim, weights, avgweights)

    def assess_cpl5_percents(self, averg, maxim, weights, avgweights):
        return self.assess_func(self.cpl_percents(5), averg, maxim, weights, avgweights)

    # Assessment Tools
    def assess_func(self, func, averg, maxim, weights, avgweights):
        flags = []
        itergames = zip(func, self.mblurs(), self.hblurs(), self.holds(), self.move_times())
        if len(self.games) > 2:
            flags.append(weighted_avg(itergames, avgweights) - averg)
        for r, mb, hb, ho, mt in itergames:
            flags.append(r - (maxim - weights_mask(weights, mb, hb, ho, mt)))
        return flags

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

    def cpl_percents(self, cp):
        return list(i.analysed.cpl_percent(cp) for i in self.games)

    def accuracy_percentages(self, cp):
        return list(i.analysed.accuracy_percentage(cp) for i in self.games)

    def scaled_accuracy_percentages(self, bound):
        return list(i.analysed.scaled_accuracy_percentage(bound) for i in self.games)

    def accuracy_percentages_20(self, cp):
        return list(i.analysed.accuracy_percentage_20(cp) for i in self.games)