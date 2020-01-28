from Assignment1.board import Board
from Assignment1.peg import Peg


class Player(object):

    def __init__(self, game=Board):
        self.game = game

    # ser for meg et move på formen [(0,0), (1,0),(2,0)]
    def make_move(self, move):
        game = self.game
        start, jump, goal = move[0], move[1], move[2]

        if not is_legal_move(game, move):
            return False  # Kanskje bare returnere brettet uten å gjøre move?

        game.board[start[0]][start[1]].filled = False
        game.board[jump[0]][jump[1]].filled = False
        game.board[goal[0]][goal[1]].filled = True

        if not more_moves_available(game):
            if game_won(game):
                return 1  # Hva skal returneres?
            else:
                return 0  # Hva hvis spillet er ferdig, men ikke vunnet?

        return game


def is_legal_move(game, move):
    start, jump, end = move[0], move[1], move[2]

    if not is_filled(game, start) or (not is_filled(game, jump)) or (is_filled(game, end)):
        return False
    elif start not in game.board[jump[0]][jump[1]].neighbours and end not in game.board[jump[0]][jump[1]].neighbours:
        return False
    elif not is_on_line(start, jump, end):
        return False

    return True


def is_filled(game, coordinates):
    if game.board[coordinates[0]][coordinates[1]].filled:
        return True

    return False


def is_on_line(start, jump, end):
    delta_row = jump[0] - start[0]
    delta_column = jump[1] - start[1]
    if end[0] == jump[0] + delta_row and end[1] == jump[1] + delta_column:
        return True

    return False


def more_moves_available(game):
    # Iterere over alle pegs i boardet:
    rows = game.board.layers - 1
    columns = rows
    for row in rows:
        for column in columns:
            if game.board[row][column].filled:
                for neigh in game.board[row][column].neighbours:
                    # Sjekke om nabo er på linje og om neste evt. nabo er utenfor index
                    if neigh.filled:
                        delta_column = neigh.coordinates[1] - column
                        delta_row = neigh.coordinates[0] - row
                        end_column = neigh.coordinates[1] + delta_column
                        end_row = neigh.coordinates[0] + delta_row
                        if (not end_column >= column or not end_row >= rows
                                or not game.board[end_row][end_column] is None):
                            if not game.board[end_row][end_column].filled:
                                return True

    return False


def game_won(game):
    # Iterere over alle pegs i boardet:
    amount_filled = 0
    rows = game.board.layers - 1
    columns = rows
    for row in rows:
        for column in columns:
            if game.board[row][column].filled:
                amount_filled += 1

    if amount_filled == 1:
        return True

    return False
