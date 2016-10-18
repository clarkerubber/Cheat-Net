class AnalysedMove:
    def __init__(self, move, evaluation):
        self.move = move
        self.evaluation = evaluation

    def __str__(self):
        return str(self.move) + ': ' + str(self.evaluation)

    def sign(self, val):
        if val <= 0:
            return -1
        else:
            return 1

    def sort_val(self):
        if self.evaluation.cp is not None:
            return self.evaluation.cp
        elif self.evaluation.mate is not None:
            return self.sign(self.evaluation.mate) * (abs(100 + self.evaluation.mate)) * 10000
        else:
            return 0