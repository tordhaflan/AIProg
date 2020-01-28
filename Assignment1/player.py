from Assignment1.board import Board, check_boundary
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
        print("a")
        return False
    elif start not in game.board[jump[0]][jump[1]].neighbours or end not in game.board[jump[0]][jump[1]].neighbours:
        print("b")
        return False
    elif not is_on_line(start, jump, end):
        print("c")
        return False
    elif (not check_boundary(start[0], start[1], game.layers, game.diamond)
            or not check_boundary(jump[0], jump[1], game.layers, game.diamond)
            or not check_boundary(end[0], end[1], game.layers, game.diamond)):
        print("c")
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
    rows = game.layers - 1
    columns = rows
    for row in range(0, rows):
        for column in range(0, columns):
            if check_boundary(row, column, game.layers, game.diamond) and game.board[row][column].filled:
                for neigh in game.board[row][column].neighbours:
                    if game.board[neigh[0]][neigh[1]].filled:
                        delta_column = neigh[1] - column
                        delta_row = neigh[0] - row
                        end_column = neigh[1] + delta_column
                        end_row = neigh[0] + delta_row
                        if check_boundary(end_row, end_column, game.layers, game.diamond):
                            if not game.board[end_row][end_column].filled:
                                return True

    return False


def game_won(game):
    # Iterere over alle pegs i boardet:
    amount_filled = 0
    rows = game.layers - 1
    columns = rows
    for row in range(0, rows):
        for column in range(0, columns):
            if game.board[row][column].filled:
                amount_filled += 1

    if amount_filled == 1:
        return True

    return False
