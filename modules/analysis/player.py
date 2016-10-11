import chess
import chess.uci
import chess.pgn
import logging
from modules.analysis.game import analysed_game, analysed_position, analysed_move
from modules.analysis.tools import avg
from modules.bcolors.bcolors import bcolors
from operator import methodcaller

class analysed_player:
    def __init__(self, name, games):
        self.name = name    # str
        self.games = games  # list(analysed_game)

    def move_errors_by_game(self):
        return sum([map(list, enumerate(i.error_difs())) for i in self.games], []) # list([move_number, error])

    def graph_games_all(self):
        [i.graph_all() for i in self.games]

def analyse_player(player, games, engine, info_handler):
    # player: str, games: list(game)
    logging.debug(bcolors.UNDERLINE + bcolors.BOLD + bcolors.WARNING + 'INVESTIGATING: ' + player + bcolors.ENDC)
    analysed_games = []

    for game in games:
        node = game

        game_id = game.headers["Site"].split('/')[-1:][0]
        logging.debug(bcolors.WARNING + "Game ID: " + game_id + bcolors.ENDC)

        if game.headers["White"].lower() == player[0].lower():
            player_colour = chess.WHITE
            logging.debug(bcolors.OKBLUE + "Player is WHITE" + bcolors.ENDC)
        else:
            player_colour = chess.BLACK
            logging.debug(bcolors.OKBLUE + "Player is BLACK" + bcolors.ENDC)

        logging.debug(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
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
                    analysed_legals.append(analysed_move(p, info_handler.info["score"][1]))

                logging.debug(bcolors.WARNING + bcolors.UNDERLINE + node.board().san(next_node.move) + bcolors.ENDC)

                analysed_legals = sorted(analysed_legals, key=methodcaller('sort_val'))
                played_move = next((x for x in analysed_legals if x.move == next_node.move), None)
                analysed_positions.append(analysed_position(played_move, analysed_legals))

                logging.debug(bcolors.OKGREEN + bcolors.UNDERLINE + 'Legal Moves' + bcolors.ENDC)
                for l in analysed_legals[:3]:
                    logging.debug(bcolors.OKGREEN + "Move: " + str(node.board().san(l.move)) + bcolors.ENDC)
                    logging.debug(bcolors.OKBLUE + "   CP: " + str(l.evaluation.cp))
                    logging.debug("   Mate: " + str(l.evaluation.mate))
                logging.debug("... and " + str(max(0, len(analysed_legals) - 3)) + " more moves" + bcolors.ENDC)

            node = next_node

        ag = analysed_game(player, game_id, analysed_positions)
        #ag.graph_rank_v_sd()
        #ag.graph_error_v_sd()
        analysed_games.append(ag)

    return analysed_player(player, analysed_games)