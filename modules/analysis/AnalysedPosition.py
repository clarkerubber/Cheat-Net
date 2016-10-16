from operator import methodcaller
from modules.analysis.tools import bounded_eval, scaled_eval

class AnalysedPosition:
    def __init__(self, played, legals):
        self.played = played # analysed_move
        self.legals = sorted(legals, key=methodcaller('sort_val'))  # list(analysed_move)
        self.best_eval = bounded_eval(self.legals[0].sort_val())
        self.best_scaled_eval = bounded_eval(scaled_eval(self.legals[0].sort_val()))

    def expected_error(self):
        return avg(list(abs(self.best_eval - bounded_eval(i.sort_val())) for i in self.legals))

    def expected_scaled_error(self):
        return avg(list(abs(self.best_scaled_eval - bounded_eval(scaled_eval(i.sort_val()))) for i in self.legals))

    def top_five_sd(self):
        return np.std(list(bounded_eval(i.sort_val()) for i in self.legals[:5])).item()

    def top_five_scaled_sd(self):
        return np.std(list(bounded_eval(scaled_eval(i.sort_val())) for i in self.legals[:5])).item()

    def actual_error(self):
        return abs(self.best_eval - bounded_eval(self.played.sort_val()))

    def actual_scaled_error(self):
        return abs(self.best_scaled_eval - bounded_eval(scaled_eval(self.played.sort_val())))

    def accuracy_less_than(self, cp):
        return self.actual_error() < cp

    def scaled_accuracy_less_than(self, bound):
        return self.actual_scaled_error() < bound

    def error_dif(self):
        return self.expected_error() - self.actual_error()

    def scaled_error_dif(self):
        return self.expected_scaled_error() - self.actual_scaled_error()

    def rank(self):
        return self.legals.index(self.played)

    def percent_error(self):
        try:
            return 100*(self.actual_error()/float(self.best_eval))
        except ZeroDivisionError:
            return 0

    def percent_scaled_error(self):
        try:
            return 100*(self.actual_scaled_error()/float(self.best_scaled_eval))
        except ZeroDivisionError:
            return 0
