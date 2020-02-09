import copy
import operator
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Assignment1.SimWorld.board import Board, check_boundary, sort_color


class Player:
    # Init Player-object
    def __init__(self, layers=3, diamond=False, open_cells=[]):
        """
        :param layers: Size of the board
        :param diamond: Type of board
        :param open_cells: List of open cells
        """
        self.game = Board(layers, diamond)
        self.move = legal_moves(self.game.diamond)
        self.counter = 0
        self.pegs_left = 0
        self.game.set_open_cells(open_cells)
        self.open_cells = open_cells

        # Copy of initial board-object for visualization purposes
        self.initial_game = copy.deepcopy(self.game)

    # Creating the binary tuple list that is used in calculations in agent.py
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

    # Gets all legal moves for a given state
    # Tuple map in order to add jump and end pegs
    def get_moves(self):
        moves = []
        for row in self.game.board:
            for peg in row:
                if peg is not None:
                    for jump, end in self.move:
                        move = [peg.coordinates, tuple(map(operator.add, peg.coordinates, jump)),
                                tuple(map(operator.add, peg.coordinates, end))]
                        if is_legal_move(self.game, move):
                            moves.append(tuple(move))
        return moves

    # The execution of a move. Changing which pegs are filled.
    def do_move(self, move):
        start, jump, goal = move[0], move[1], move[2]

        self.game.board[start[0]][start[1]].filled = False
        self.game.board[jump[0]][jump[1]].filled = False
        self.game.board[goal[0]][goal[1]].filled = True

        return self.get_binary_board()

    # Check if ane more legal moves are available. If not, game_over.
    def game_over(self):
        if more_moves_available(self.game):
            return False
        return True

    # Returns a reward of 1 if only 1 peg left. Else a negative reward of pegs left divided by
    # total pegs on the initial board
    def get_reward(self):
        self.pegs_left = 0
        for row in self.game.board:
            for element in row:
                if element is not None and element.filled:
                    self.pegs_left += 1

        # For visualization purposes
        self.game = copy.deepcopy(self.initial_game)

        # If triangle, different number of original pegs than if diamond
        if not self.game.diamond:
            reward = -self.pegs_left / (((self.initial_game.layers ** 2)/2) + (self.initial_game.layers / 2))
            return (1, self.pegs_left) if self.pegs_left == 1 else (reward, self.pegs_left)
        else:
            return (1, self.pegs_left) if self.pegs_left == 1 else (
                    -self.pegs_left / self.initial_game.layers ** 2, self.pegs_left)

    # The function that updates the board.
    def update(self, num, G, actions, ax1, ax2, ax3, ax4, fig, pegs_left, parameters):
        # Resetting the plot.
        if self.counter < len(actions) + 2:
            ax2.clear()
        color_map = {}
        border_color = {}

        # Coloring pegs. Shown on first and second last plot.
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
            if self.counter == 0:
                pos = nx.get_node_attributes(G, 'pos')
                color, border = sort_color(pos, color_map, border_color)
                nx.draw_networkx(G, pos=pos, node_color=color, edgecolors=border, with_labels=False, ax=ax1)
                ax1.set_title("Initial board", fontweight='bold')

            # Feedback on the second last plot
            if self.pegs_left == 1 and self.counter == len(actions) + 1:
                ax2.set_title("Congratulation - The RL made it")
            elif self.counter == len(actions) + 1:
                ax2.set_title("The RL failed")

        # Game animation for every plot other than first, and the two last.
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
            self.do_move(move)

        # Making th final board and statistics
        if self.counter == len(actions) + 2:
            ax1.change_geometry(2, 3, 1)
            ax2.change_geometry(2, 3, 2)
            ax3.change_geometry(2, 1, 2)
            ax4.change_geometry(2, 3, 3)
            ax2.set_title("Final board", fontweight='bold')
            x = np.arange(len(pegs_left))
            ax3.set_title("Development of RLs performance", fontweight='bold')
            ax3.set_xlabel("Episodes", fontweight='semibold')
            ax3.set_ylabel("Pegs left", fontweight='semibold')
            ax3.plot(x, pegs_left)
            plot_parameters(ax4, parameters)
            ax1.set_visible(True)
            ax3.set_visible(True)
            ax4.set_visible(True)

        # Changes in the graph during the game.
        else:
            pos = nx.get_node_attributes(G, 'pos')
            color, border = sort_color(pos, color_map, border_color)
            nx.draw_networkx(G, pos=pos, node_color=color, edgecolors=border, with_labels=False, ax=ax2)
            self.counter += 1
            fig.canvas.set_window_title('Peg Solitaire - RL')

    # Plot if the game has no legal initial moves
    def show_illegal_game(self, G, actions, ax1, ax2, ax3, ax4, fig, parameters):
        color_map = {}
        border_color = {}
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

        pos = nx.get_node_attributes(G, 'pos')
        color, border = sort_color(pos, color_map, border_color)
        nx.draw_networkx(G, pos=pos, node_color=color, edgecolors=border, with_labels=False, ax=ax1)
        ax1.set_title("Initial board", fontweight='bold')

        length = len(self.open_cells)

        for i, x in enumerate(self.open_cells):
            row = 1/(length+1)
            if i == 0:
                ax2.text(0, 1 - row, "Open cell" + (": " + str(x) if length == 1 else "s: " + str(x)),
                         fontweight='bold', fontsize=24)
            else:
                ax2.text(0.505, 1 - (row*(i+1)), str(x), fontweight='bold', fontsize=24)
        ax2.axis('off')
        ax3.text(0.3, 0.5, "This bord has no initial move", fontweight='bold', fontsize=24)
        ax3.axis('off')
        plot_parameters(ax4, parameters)

        ax1.change_geometry(2, 3, 1)
        ax2.change_geometry(2, 3, 2)
        ax3.change_geometry(2, 1, 2)
        ax4.change_geometry(2, 3, 3)
        ax1.set_visible(True)
        ax3.set_visible(True)
        ax4.set_visible(True)

    # Animating the game
    def show_game(self, actions, pegs_left, parameters, legal_game):
        # Making the plots shown in the end
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(20, 11.2))
        # Hiding them until last plot
        ax1.set_visible(False)
        ax3.set_visible(False)
        ax4.set_visible(False)
        ax2.change_geometry(1, 1, 1)

        # Builds the structure of the board
        G = nx.Graph()
        for b in self.game.board:
            for i in range(len(b)):
                peg = b[i]
                if peg is not None:
                    G.add_node(peg.pegNumber, pos=peg.drawing_coordinates)
                    for x, y in peg.neighbours:
                        G.add_edge(peg.pegNumber, self.game.board[x][y].pegNumber)

        # The animation of the game, if there is a legal first move
        if legal_game:
            ani = FuncAnimation(fig, self.update, frames=(len(actions) + 2),
                            fargs=(G, actions, ax1, ax2, ax3, ax4, fig, pegs_left, parameters),
                            interval=200, repeat=False)
        else:
            self.show_illegal_game(G, actions, ax1, ax2, ax3, ax4, fig, parameters)
        plt.show()




# Finding coordinates of possible moves
def legal_moves(diamond):
    moves = [[(-1, 0), (-2, 0)], [(1, 0), (2, 0)], [(0, -1), (0, -2)], [(0, 1), (0, 2)]]

    if diamond:
        moves.append([(-1, 1), (-2, 2)])
        moves.append([(1, -1), (2, -2)])
    else:
        moves.append([(-1, -1), (-2, -2)])
        moves.append([(1, 1), (2, 2)])

    return moves


# Checking if a move is legal
def is_legal_move(game, move):
    start, jump, end = move[0], move[1], move[2]

    # Checking boundaries of the board
    if (not check_boundary(start[0], start[1], game.layers, game.diamond)
            or not check_boundary(jump[0], jump[1], game.layers, game.diamond)
            or not check_boundary(end[0], end[1], game.layers, game.diamond)):
        return False

    # Checking if "jump" is neighbour of both "start" and "end"
    elif start not in game.board[jump[0]][jump[1]].neighbours or end not in game.board[jump[0]][jump[1]].neighbours:
        return False

    # Checking if the pegs are on line
    elif not is_on_line(start, jump, end):
        return False

    # Checking the fill criteria
    elif not is_filled(game, start) or (not is_filled(game, jump)) or (is_filled(game, end)):
        return False

    return True


# Checking if peg in coordinates is filled
def is_filled(game, coordinates):
    if game.board[coordinates[0]][coordinates[1]].filled:
        return True

    return False


# Checking if coordinates are on line
def is_on_line(start, jump, end):
    delta_row = jump[0] - start[0]
    delta_column = jump[1] - start[1]
    if end[0] == jump[0] + delta_row and end[1] == jump[1] + delta_column:
        return True

    return False


# Checking if there are more possible moves on the board
def more_moves_available(game):
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


# Parameters for the final plot
def plot_parameters(ax, parameters):
    ax.text(0.05, 1, "Parameters:", fontsize=14, fontweight='bold')
    ax.text(0.05, 0.9, ("Number of episodes: " + str(parameters[3])), fontsize=12)
    ax.text(0.05, 0.8, ("Initial epsilon (\u03B5): " + str(parameters[12])), fontsize=12)
    ax.text(0.05, 0.7, ("Actor - learning rate ($\u03B1_a$): " + str(parameters[6])), fontsize=12)
    ax.text(0.05, 0.6, ("Actor - eligibility decay rate ($\u03BB_a$): " + str(parameters[8])), fontsize=12)
    ax.text(0.05, 0.5, ("Actor - discount factor ($\u03B3_a$): " + str(parameters[10])), fontsize=12)
    ax.text(0.05, 0.4, ("Critic - learning rate ($\u03B1_c$): " + str(parameters[7])), fontsize=12)
    ax.text(0.05, 0.3, ("Critic - eligibility decay rate ($\u03BB_c$): " + str(parameters[9])), fontsize=12)
    ax.text(0.05, 0.2, ("Critic - discount factor ($\u03B3_c$): " + str(parameters[11])), fontsize=12)
    ax.text(0.05, 0.1, "Type of critic: ", fontsize=12)
    if parameters[4] == 'table':
        ax.text(0.325, 0.1, "Table", fontweight='semibold', fontsize=12)
    else:
        ax.text(0.325, 0.1, "Neural Network", fontweight='semibold', fontsize=12)
        ax.text(0.05, 0, ("Layer structure-NN: " + str(parameters[5])), fontsize=12)

    ax.axis('off')
