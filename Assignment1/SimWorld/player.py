import copy

from Assignment1.SimWorld.board import Board, check_boundary, draw_board, draw_board_final
import random


class Player(object):

    #Må skrives om slik at den tar inn parametere og lager et board objekt selv
    def __init__(self, game=Board, open_cells=[]):
        self.initial_game = copy.deepcopy(game)
        self.game = game
        self.move = legal_moves(self.game.diamond)

        self.game.set_open_cells(open_cells) #endres når vi initialiserer player objektet med et board -> sendes da som en inputverdi

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

    def get_binary_board(self):
        board = []
        for row in self.game.board:
            for element in row:
                if element.filled:
                    board.append(1)
                else:
                    board.append(0)
        return tuple(board)

    def get_moves(self):
        moves = []
        for row in self.game.board:
            for peg in row:
                for r, c in self.move:
                    move = [peg.coordinates, r, c]
                    if is_legal_move(move):
                        moves.append(move)
        return moves

    def do_move(self, move):
        start, jump, goal = move[0], move[1], move[2]

        self.game.board[start[0]][start[1]].filled = False
        self.game.board[jump[0]][jump[1]].filled = False
        self.game.board[goal[0]][goal[1]].filled = True

        return self.get_binary_board()

    def won(self):
        if not more_moves_available(self.game):
            if game_won(self.game):
                self.game = copy.deepcopy(self.initial_game)
                return True  # Hva skal returneres?
            else:
                return False  # Hva hvis spillet er ferdig, men ikke vunnet?


def legal_moves(diamond):
    moves = [[(-1, 0), (-2, 0)], [(1, 0), (2, 0)], [(0, -1), (0, -1)], [(0, 1), (0, 2)]]

    if diamond:
        moves.append([(-1, 1), (-2, 2)])
        moves.append([(1, -1), (2, -2)])
    else:
        moves.append([(-1, -1), (-2, -2)])
        moves.append([(1, 1), (2, 2)])
    return moves



def is_legal_move(game, move):
    start, jump, end = move[0], move[1], move[2]

    if (not check_boundary(start[0], start[1], game.layers, game.diamond)
            or not check_boundary(jump[0], jump[1], game.layers, game.diamond)
            or not check_boundary(end[0], end[1], game.layers, game.diamond)):
        return False
    elif start not in game.board[jump[0]][jump[1]].neighbours or end not in game.board[jump[0]][jump[1]].neighbours:
        return False
    elif not is_on_line(start, jump, end):
        return False
    elif not is_filled(game, start) or (not is_filled(game, jump)) or (is_filled(game, end)):
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
    rows = game.layers
    columns = rows
    for row in range(rows):
        for column in range(columns):
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
    rows = game.layers
    columns = rows
    for row in range(0, rows):
        for column in range(0, columns):
            if check_boundary(row, column, game.layers, game.diamond):
                if game.board[row][column].filled:
                    amount_filled += 1

    if amount_filled == 1:
        return True

    return False


layers = 8

B = Board(layers)

P = Player(B)

if not B.diamond:
    row = random.randint(0, layers - 1)
    column = random.randint(0, row)
    open_cell = (row, column)
else:
    open_cell = (random.randint(0, layers - 1), random.randint(0, layers - 1))

P.game.board[open_cell[0]][open_cell[1]].filled = False

draw_board_final(P.game)

# print(more_moves_available(P.game))

while more_moves_available(P.game):
    r = random.randint(0, layers - 1)
    c = random.randint(0, layers - 1)
    peg = P.game.board[r][c]
    if peg is not None:
        neigh = peg.neighbours[random.randint(0, len(peg.neighbours) - 1)]
        delta_r = neigh[0] - r
        delta_c = neigh[1] - c
        move = [(r, c), (r + delta_r, c + delta_c), (r + 2 * delta_r, c + 2 * delta_c)]
        if is_legal_move(P.game, move):
            draw_board(P.game, move[0], move[1])
            P.make_move(move)

draw_board_final(P.game)
print(game_won(P.game))
