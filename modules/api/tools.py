import chess.pgn
from os import walk
from os.path import join

def get_files(dir):
    return [x[2] for x in walk(dir)][0]

def get_folders(dir):
    return map(lambda x: [x.split('/')[-1], x], [x[0] for x in walk(dir)])[1:]

def get_player_games(player):
    game_files = get_files(player)
    games = []
    for game_file in game_files:
        pgn = open(join(player, game_file))
        games.append(chess.pgn.read_game(pgn))
        pgn.close()
    return games
