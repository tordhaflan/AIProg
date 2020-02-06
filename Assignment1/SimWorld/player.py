import copy
import operator
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Assignment1.SimWorld.board import Board, check_boundary, sort_color


class Player:

    # Må skrives om slik at den tar inn parametere og lager et board objekt selv
    def __init__(self, game=Board, open_cells=[]):

        self.initial_game = copy.deepcopy(game)
        self.game = game
        self.move = legal_moves(self.game.diamond)
        self.counter = 0
        self.pegs_left = 0

        self.game.set_open_cells(open_cells)
        self.initial_game.set_open_cells(open_cells)  # endres når vi initialiserer player objektet med et board -> sendes da som en inputverdi

    # ser for meg et move på formen [(0,0), (1,0),(2,0)]
    def make_move(self, move):
        # game = self.game
        start, jump, goal = move[0], move[1], move[2]

        if not is_legal_move(self.game, move):
            return False  # Kanskje bare returnere brettet uten å gjøre move?

        self.game.board[start[0]][start[1]].filled = False
        self.game.board[jump[0]][jump[1]].filled = False
        self.game.board[goal[0]][goal[1]].filled = True

        if not more_moves_available(self.game):
            if game_won(self.game):
                return 1  # Hva skal returneres?
            else:
                return 0  # Hva hvis spillet er ferdig, men ikke vunnet?

        return self.game

    def get_binary_board(self):
        board = []
        for row in self.game.board:
            for element in row:
                if element is None:
                    board.append(0)
                elif element.filled:
                    board.append(1)
                else:
                    board.append(0)
        return tuple(board)

    def get_moves(self):
        moves = []
        check = [(3, 3), (2, 2), (1, 1)]
        for row in self.game.board:
            for peg in row:
                if peg is not None:
                    for r, c in self.move:
                        move = [peg.coordinates, tuple(map(operator.add, peg.coordinates, r)),
                                tuple(map(operator.add, peg.coordinates, c))]
                        if is_legal_move(self.game, move):
                            moves.append(tuple(move))
        return moves

    def do_move(self, move):
        start, jump, goal = move[0], move[1], move[2]

        self.game.board[start[0]][start[1]].filled = False
        self.game.board[jump[0]][jump[1]].filled = False
        self.game.board[goal[0]][goal[1]].filled = True

        return self.get_binary_board()

    def game_over(self):
        if more_moves_available(self.game):
            return False
        return True  # Hva skal returneres?

    def get_reward(self):
        self.pegs_left = 0
        for row in self.game.board:
            for element in row:
                if element is not None and element.filled:
                    self.pegs_left += 1
        self.game = copy.deepcopy(self.initial_game)
        return (1,self.pegs_left) if self.pegs_left == 1 else (-self.pegs_left / self.initial_game.layers ** 2, self.pegs_left)  # kanskje skrive om else for triangel

    def update(self, num, G, actions, ax1, ax2, fig, pegs_left):
        if self.counter < len(actions) + 2:
            ax1.clear()
        color_map = {}
        border_color = {}

        if self.counter == 0 or self.counter == len(actions) + 1:
            for b in self.game.board:
                for i in range(len(b)):
                    peg = b[i]
                    if peg is not None:
                        if peg.filled:
                            color_map[peg.pegNumber] = 'darkblue'
                            border_color[peg.pegNumber] = 'darkblue'
                        else:
                            color_map[peg.pegNumber] = 'white'
                            border_color[peg.pegNumber] = 'grey'
            if self.pegs_left == 1 and self.counter == len(actions) + 1:
                ax1.set_title("Congratulation - The RL made it")

            elif self.counter == len(actions) + 1:
                ax1.set_title("The RL failed")
                ax1.change_geometry(1, 2, 1)


        elif self.counter < len(actions) + 2:
            move = actions[self.counter - 1]
            start = move[0]
            jump = move[1]
            for index, b in enumerate(self.game.board):
                for i in range(len(b)):
                    peg = b[i]
                    if peg is not None:
                        if peg.coordinates == start:
                            color_map[peg.pegNumber] = 'green'
                            border_color[peg.pegNumber] = 'green'
                        elif peg.coordinates == jump:
                            color_map[peg.pegNumber] = 'darkred'
                            border_color[peg.pegNumber] = 'darkred'
                        elif peg.filled:
                            color_map[peg.pegNumber] = 'darkblue'
                            border_color[peg.pegNumber] = 'darkblue'
                        else:
                            color_map[peg.pegNumber] = 'white'
                            border_color[peg.pegNumber] = 'grey'
            self.make_move(move)

        if self.counter == len(actions) + 2:
            ax1.change_geometry(1, 2, 1)
            ax1.set_title("Final board")
            x = np.arange(len(pegs_left))
            ax2.set_title("Statistics over pegs left")
            ax2.set_xlabel("Episodes")
            ax2.set_ylabel("Pegs left")
            ax2.plot(x, pegs_left)
            ax2.set_visible(True)
        else:
            pos = nx.get_node_attributes(G, 'pos')
            color, border = sort_color(pos, color_map, border_color)
            nx.draw_networkx(G, pos=pos, node_color=color, edgecolors=border, with_labels=False, ax=ax1)
            self.counter += 1
            fig.canvas.set_window_title('Peg Solitaire - RL')



    def show_game(self, actions, pegs_left):
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(13, 11))
        ax2.set_visible(False)
        ax1.change_geometry(1, 1, 1)


        G = nx.Graph()
        for b in self.game.board:
            for i in range(len(b)):
                peg = b[i]
                if peg is not None:
                    G.add_node(peg.pegNumber, pos=peg.drawing_coordinates)
                    for x, y in peg.neighbours:
                        G.add_edge(peg.pegNumber, self.game.board[x][y].pegNumber)

        ani = FuncAnimation(fig, self.update, frames=(len(actions) + 2), fargs=(G, actions, ax1, ax2, fig, pegs_left),
                            interval=2000, repeat=False)
        plt.show()


def legal_moves(diamond):
    moves = [[(-1, 0), (-2, 0)], [(1, 0), (2, 0)], [(0, -1), (0, -2)], [(0, 1), (0, 2)]]

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
