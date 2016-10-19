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
                    engine.go(nodes=1000000)
                    analysed_legals.append(AnalysedMove(p, info_handler.info["score"][1]))

                logging.debug(bcolors.WARNING + bcolors.UNDERLINE + node.board().san(next_node.move) + bcolors.ENDC)

                analysed_legals = sorted(analysed_legals, key=methodcaller('sort_val'))
                played_move = next((x for x in analysed_legals if x.move == next_node.move), None)
                analysed_positions.append(AnalysedPosition(played_move, analysed_legals))

                logging.debug(bcolors.OKGREEN + bcolors.UNDERLINE + 'Legal Moves' + bcolors.ENDC)
                for l in analysed_legals[:3]:
                    logging.debug(bcolors.OKGREEN + "Move: " + str(node.board().san(l.move)) + bcolors.ENDC)
                    logging.debug(bcolors.OKBLUE + "   CP: " + str(l.evaluation.cp))
                    logging.debug("   Mate: " + str(l.evaluation.mate))
                logging.debug("... and " + str(max(0, len(analysed_legals) - 3)) + " more moves" + bcolors.ENDC)

            node = next_node

        self.analysed = AnalysedGame(self.assessment, analysed_positions)

def recent_games(assessments, pgns):
    assessments = sorted(
        filter(lambda x: x.assessment > 2,
            sorted(assessments,
                key=attrgetter('date'),
                reverse=True)[:100]),
        key=attrgetter('assessment'),
        reverse=True)[:6]
    try:
        return [AnalysableGame(a, pgns[a.gameId]) for a in assessments]
    except ValueError:
        return []