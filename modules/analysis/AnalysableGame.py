import logging
import chess

from operator import attrgetter, methodcaller
from modules.bcolors.bcolors import bcolors
from modules.analysis.AnalysedGame import AnalysedGame
from modules.analysis.AnalysedPosition import AnalysedPosition
from modules.analysis.AnalysedMove import AnalysedMove

class AnalysableGame:
    def __init__(self, assessment, pgn):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        self.assessment = assessment # PlayerAssessment
        self.game = chess.pgn.read_game(StringIO(pgn['pgn']))
        self.analysed = None

    def analyse(self, engine, info_handler):
        node = self.game

        logging.debug(bcolors.WARNING + "Game ID: " + self.assessment.gameId + bcolors.ENDC)
        player_colour = self.assessment.white

        logging.debug(bcolors.OKGREEN + "Game Length: " + str(node.end().board().fullmove_number))
        logging.debug("Analysing Game..." + bcolors.ENDC)

        engine.ucinewgame()

        analysed_positions = []

        while not node.is_end():
            next_node = node.variation(0)
            engine.position(next_node.board())

            if player_colour == node.board().turn:
                analysed_legals = []

                for p in node.board().legal_moves:
                    position_copy = node.board().copy()
                    position_copy.push(p)
                    engine.position(position_copy)
                    engine.go(nodes=800000)
                    analysed_legals.append(AnalysedMove(p, info_handler.info["score"][1]))

                analysed_legals = sorted(analysed_legals, key=methodcaller('sort_val'))
                played_move = next((x for x in analysed_legals if x.move == next_node.move), None)
                analysed_positions.append(AnalysedPosition(played_move, analysed_legals))

            node = next_node

        self.analysed = AnalysedGame(self.assessment, analysed_positions)

def recent_games(assessments, pgns):
    try:
        assessments = sorted(assessments, key = lambda x: (attrgetter('assessment'), attrgetter('date')), reverse=True)
        return list(AnalysableGame(a, pgns[a.gameId]) for a in assessments if pgns[a.gameId].get('variant', False) == False)[:5]
    except ValueError:
        return []
    except IndexError:
        return []