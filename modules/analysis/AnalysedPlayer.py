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
        self.games = games  # list(AnalysedGame)
        self.gamesPlayed = gamesPlayed # # of games played
        self.cheater = cheater # True, False, None
        self.related = related # list(userId)

    def move_errors_by_game(self):
        return sum([map(list, enumerate(i.error_difs())) for i in self.games], []) # list([move_number, error])

    def graph_games_all(self):
        [i.graph_all() for i in self.games]

    def graph_error_v_move_no(self):
        x = sum(list(i.move_numbers() for i in self.games), [])
        y = sum(list(i.actual_errors() for i in self.games), [])

        avgs = []
        for t in range(max(*x)):
            l = []
            for xt, yt in zip(x, y):
                if xt == t:
                    l.append(yt)
            avgs.append(avg(l))

        fig, ax = plt.subplots()
        ax.plot(list(range(max(*x))), avgs, 'r-')
        ax.set_xlabel('move number')
        ax.set_ylabel('avg error')
        return fig

    def error_v_move_no(self):
        x = sum(list(i.move_numbers() for i in self.games), [])
        y = sum(list(i.actual_errors() for i in self.games), [])

        avgs = []
        for t in range(max(*x)):
            l = []
            for xt, yt in zip(x, y):
                if xt == t:
                    l.append(yt)
            avgs.append(avg(l))

        return (x, y)

    def ranks(self):
        return sum(list(i.ranks() for i in self.games), [])

    def rank_0_percents(self):
        return list(i.rank_0_percent() for i in self.games)

    def rank_01_percents(self):
        return list(i.rank_01_percent() for i in self.games)

    def rank_0_1030_percents(self):
        return list(i.rank_0_1030_percent() for i in self.games)

    def rank_5more_percents(self):
        return list(i.rank_5more_percent() for i in self.games)

    def accuracy_percentages(self, cp):
        return list(i.accuracy_percentage(cp) for i in self.games)

    def accuracy_percentages_20(self, cp):
        return list(i.accuracy_percentage_20(cp) for i in self.games)

    def tactics_seized(self):
        a = list(i.tactics_seized() for i in self.games)
        tactics_seized = sum(list(i[0] for i in a))
        total_tactics = sum(list(i[1] for i in a))
        if total_tactics > 10:
            return 100*tactics_seized/float(total_tactics)
        else:
            return 0

    def graph_merged(self):
        x = sum(list(i.top_five_sds() for i in self.games),[])
        x2 = sum(list(i.move_numbers() for i in self.games),[])
        y1 = sum(list(i.ranks() for i in self.games), [])
        y2 = sum(list(i.actual_errors() for i in self.games), [])
        y3 = sum(list(i.percent_errors() for i in self.games), [])

        fig, ax = plt.subplots()
        avgs = []
        for t in range(max(*x2)):
            l = []
            for x, y in zip(x2, y2):
                if x == t:
                    l.append(y)
            avgs.append(avg(l))

        ax.scatter(x2, y2)
        ax.plot(list(range(max(*x2))), avgs, 'r--')
        ax.set_xlabel('move number')
        ax.set_ylabel('move error')
        fig.savefig('figures/'+self.name+'_MoveNoVError.svg')
        fig.show()
