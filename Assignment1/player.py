from Assignment1.board import Board
from Assignment1.peg import Peg


class Player(object):

    def __init__(self, game=Board):
        self.game = game

    # ser for meg et move på formen [[0,0], [1,0], [2,0]]
    def make_move(self, move):
        game = self.board
        start, jump, goal = move[0], move[1], move[2]

        if not is_legal_move(game, move):
            return False  # Kanskje bare returnere brettet uten å gjøre move?

        game.board[start[0]][start[1]].filled = False
        game.board[jump[0]][jump[1]].filled = False
        game.board[goal[0]][goal[1]].filled = True

        #Sjekke om det finnes flere legal moves og evt. om det bare er en filled igjen.

        if not more_moves_available(game):
            if game_won(game):
                return 1 # Hva skal returneres?
            else:
                return 2 # Hva returneres hvis spillet er ferdig, men ikke vunnet?


        return game


def is_legal_move(game=Board, move=[]):
    start, jump, end = move[0], move[1], move[2]

    if not is_filled(game, start) or (not is_filled(game, jump)) or (is_filled(game, end)):
        return False
    elif start not in game.board[jump[0]][jump[1]].neighbours and end not in game.board[jump[0]][jump[1]].neighbours:
        return False


    # Hvis ikke nabo (done) og sjekke om de er på rekke

    return True


def is_filled(game=Board, coordinates=[]):
    if game.board[coordinates[0]][coordinates[1]].filled:
        return True

    return False


def more_moves_available(game):
    # Iterere over alle pegs i boardet:
    pegs = game.board
    for peg in range(1, pegs):
        if peg.filled:
            for neigh in peg.neighbours:
                if neigh.filled:



    return True


def game_won(game):
    # Iterere over alle pegs i boardet:
    pegs = game.board
    amount_filled = 0
    for peg in range(1, pegs):
        if peg.filled:
            amount_filled += 1

    if amount_filled == 1:
        return True

    return False

