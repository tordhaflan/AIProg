import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import copy


class Hex:
    def __init__(self, layers=3):
        """ Initialize  Board-object

        :param layers: Size of the board
        :param diamond: Type of board
        """
        self.layers = layers
        self.board = make_graph(self.layers)
        self.set_neighbours()
        self.final_path = []
        self.winner = None

    def set_neighbours(self):
        """
        Sets the neighbours of a peg
        """
        for i in range(self.layers):
            for j in range(self.layers):
                if self.board[i][j] is not None:
                    n = find_neighbourhood(i, j, self.layers)
                    self.board[i][j].set_neighbours(n)

    def child_actions(self, state, player):
        """
        Finding the possible action for a state
        """
        moves = []
        for i, s in enumerate(state):
            if s == 0:
                moves.append((i, player))
        return moves

    def reset_game(self):
        """ To initialize the open cells in the board

        :param open_cells: list of tuples, coordinates of open cells
        """
        for r in range(self.layers):
            for c in range(self.layers):
                self.board[r][c].filled = 0

    def do_move(self, action, player):
        """
        Doing a actual move in a played game
        """
        row = int(np.floor(action/self.layers))
        col = action % self.layers
        if self.board[row][col].filled == 0:
            self.board[row][col].filled = player

    def do_action(self, state, action, player):
        """
        Doing a move on a input state (for simulation)
        """
        state[action] = player
        return state

    def get_board(self):
        """
        :return current state
        """
        state = []
        for r in range(self.layers):
            for c in range(self.layers):
                state.append(self.board[r][c].filled)
        return state

    def game_over(self, state):
        """
        Checking if a state is a winning state
        """

        top = [(0, i) for i in range(self.layers)]
        bottom = [(self.layers-1, i) for i in range(self.layers)]
        if self.winning(1, top, bottom, state):
            return True
        else:
            top = [(i, 0) for i in range(self.layers)]
            bottom = [(i, self.layers - 1) for i in range(self.layers)]

            return True if self.winning(2, top, bottom, state) else False

    def winning(self, player, top, bottom, state):
        """
        Helping method for game_over
        """

        for r, c in top:
            for r2, c2 in bottom:
                visited = [[False for r in range(self.layers)] for c in range(self.layers)]
                if state[r*self.layers+c] == player and state[r2*self.layers+c2] == player:
                    queue = []
                    path = []

                    queue.append((r, c))
                    path.append((r, c))
                    visited[r][c] = True
                    while queue:
                        n = queue.pop(0)
                        if n[0] == r2 and n[1] == c2:
                            path.append(n)
                            self.final_path = path
                            self.winner = player
                            return True

                        for i, j in self.board[n[0]][n[1]].neighbours:
                            if visited[i][j] is False and state[i*self.layers+j] == player \
                                    and self.board[i][j].coordinates not in top:
                                queue.append((i, j))
                                visited[i][j] = True
                        path.append(n)
        return False

    def draw(self, player, itt1=1, itt2=2):
        """
        Displaing a game/state
        """
        if len(self.final_path) != 0:
            self.a_star()
        draw_board(self.board, player, self.final_path, itt1, itt2)

    def initial_game(self):
        board = self.get_board()
        if board.__contains__(1) or board.__contains__(2):
            return False
        return True


    def a_star(self):
        frontier = [] #coordinates, g_score
        came_from = {}
        g_score = {}
        f_score = {}

        start = self.final_path.pop(0)
        end = self.final_path[-1]

        g_score[start] = 0
        f_score[start] = abs(start[0]-end[0]) + abs(start[1] + end[1])

        frontier.append((start, f_score[start]))

        while len(frontier) > 0:
            frontier.sort(key=lambda tup: tup[1])
            current = frontier.pop(-1)[0]

            if current == end:
                new_path = [current]
                while current in came_from.keys():
                    current = came_from[current]
                    new_path.append(current)
                new_path.reverse()
                self.final_path = new_path

            for n in self.board[current[0]][current[1]].neighbours:
                if self.final_path.__contains__(n):
                    g = g_score[current] + abs(n[0]-current[0]) + abs(n[1] + current[1])
                    if n not in g_score.keys():
                        g_score[n] = 100
                    if g < g_score[n]:
                        came_from[n] = current
                        g_score[n] = g
                        f_score[n] = g_score[n] + abs(n[0]-end[0]) + abs(n[1] + end[1])
                        if not frontier.__contains__((n, f_score[n])):
                            frontier.append((n, f_score[n]))




class Peg:

    def __init__(self, x, y, row, col, number, filled=0):
        """ Initialize Peg-object

        :param x: x-coordinate
        :param y: y-coordinate
        :param row: row-number
        :param col: row-number
        :param number: peg-number
        :param filled: if peg is filled or not
        """
        self.drawing_coordinates = (x, y)
        self.coordinates = (row, col)
        self.neighbours = []
        self.filled = filled
        self.pegNumber = number
        self.player = 0

    def set_neighbours(self, neighbours):
        """ Appends neighbouring peg to the list of neighbours

        :param neighbours: a list of neighbouring Pegs
        """
        for n in neighbours:
            self.neighbours.append(n)


def make_graph(layers):
    """ To make the board itself.

    :param layers: int, Size of the board
    :param diamond: boolean, Type of board
    :return: A list of Peg-objects
    """

    row = 2 * layers - 1

    graph = [[None for x in range(layers)] for y in range(layers)]
    n = 1
    for i in range(row):
        if i < layers:
            k = 0
            col = 0
            for j in range(layers - i - 1):
                k += 1
            for j in range(i + 1):
                graph[i - j][j] = Peg(k, row - i - 1, i - col, col, n)
                n += 1
                k += 2
                col += 1
        else:
            k = 0
            col = 1
            for j in range(i - layers + 1, 0, -1):
                k += 1
            for j in range(row - i):
                graph[layers - j - 1][i - layers + j + 1] = Peg(k, row - i - 1, layers - col, i - layers + col, n)
                n += 1
                k += 2
                col += 1

    return graph


def find_neighbourhood(row, col, layers):
    """ Finds all the neighbours of a peg that set_neighbours then sets.

    :param row: int, row coordinate
    :param col: int, col coordinate
    :return: list of tuples, all neighbouring coordinates that are legal
    """
    neighbourhood = []
    for i in range(6):
        if check_boundary(row - 1, col, layers) and i == 0:
            neighbourhood.append((row - 1, col))
        elif check_boundary(row + 1, col, layers) and i == 1:
            neighbourhood.append((row + 1, col))
        elif check_boundary(row, col - 1, layers) and i == 2:
            neighbourhood.append((row, col - 1))
        elif check_boundary(row, col + 1, layers) and i == 3:
            neighbourhood.append((row, col + 1))
        elif check_boundary(row - 1, col + 1, layers) and i == 4:
            neighbourhood.append((row - 1, col + 1))
        elif check_boundary(row + 1, col - 1, layers) and i == 5:
            neighbourhood.append((row + 1, col - 1))

    return neighbourhood


def sort_color(pos, color_map, border_color):
    """ Sorts the graph in the manner that networkx prefers.

    :param pos: Node attribute position
    :param color_map: Dict of pegnumbers and colors for nodes
    :param border_color: Dict of pegnumbers and colors for node borders
    :return: new_map and new_border sorted on pegnumbers
    """
    new_map = []
    new_border = []
    for key in pos.keys():
        new_map.append(color_map[key])
        new_border.append(border_color[key])

    return new_map, new_border


def check_boundary(row, col, layers):
    """ Checks if a tuple of coordinates is within the boundaries of the board.

    :param row: row coordinate
    :param col: col coordinate
    :param layers: size
    :return: True if the coordinates is within the boundaries of the board
    """
    if row < 0 or col < 0:
        return False
    elif row >= layers or col >= layers:
        return False
    return True


def draw_board(board, winner=1, final_path=[], itt1 = None, itt2 = None):
    """ Just in case we are asked to display a board on the demo.

    :param final_path:
    :param winner:
    :param board: the Board-object
    :return: Displays a board
    """
    G = nx.Graph()
    color_map = {}
    border_color = {}
    edge_color = 'b' if winner == 1 else 'r'
    for b in board:
        for i in range(len(b)):
            peg = b[i]
            if peg is not None:
                G.add_node(peg.pegNumber, pos=peg.drawing_coordinates)
                if peg.filled == 1:
                    color_map[peg.pegNumber] = 'darkblue'
                    border_color[peg.pegNumber] = 'darkblue'
                elif peg.filled == 2:
                    color_map[peg.pegNumber] = 'red'
                    border_color[peg.pegNumber] = 'red'
                else:
                    color_map[peg.pegNumber] = 'white'
                    border_color[peg.pegNumber] = 'grey'

                for x, y in peg.neighbours:
                    if peg.coordinates in final_path and (x,y) in final_path:
                        G.add_edge(peg.pegNumber, board[x][y].pegNumber, color=edge_color, weight=2)
                    else:
                        G.add_edge(peg.pegNumber, board[x][y].pegNumber, color ='grey', weight=1)
    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    weights = [G[u][v]['weight'] for u, v in edges]
    pos = nx.get_node_attributes(G, 'pos')
    color, border = sort_color(pos, color_map, border_color)
    nx.draw_networkx(G, pos, node_color=color, edgecolors=border, edges=edges, edge_color=colors, width=weights, with_labels=False)
    #Printing of itteration labels
    if itt1 is not None and itt2 is not None:
        if itt1 == 1 and itt2 == 2:
            s1 = "Player " + str(itt2)
            s2 = "Player " + str(itt1)
        else:
            s1 = "Itteration " + str(itt2)
            s2 = "Itteration " + str(itt1)
        h = max(max(list(pos.values())))
        if h == 4:
            v = h - 0.15
        else:
            v = h - 1
        plt.text(0, v, s=s1, fontsize=16, color='black',  horizontalalignment='left', bbox=dict(facecolor='white', edgecolor='red', pad=5.0))
        plt.text(h, v, s=s2, fontsize=16, color='black', horizontalalignment='right', bbox=dict(facecolor='white', edgecolor='blue', pad=5.0))
    #Background on board
    plt.gca().set_facecolor('ghostwhite')
    plt.show()
    plt.pause(0.2)



"""
h = Hex(4)
h.do_move(3,1)
h.do_move(7,1)
h.do_move(9,1)
h.do_move(10,1)
h.do_move(11,1)
h.do_move(12,2)
h.do_move(13,2)
h.do_move(14,2)
h.do_move(15,2)

h.game_over(h.get_board())

h.draw(h.winner, 10, 20)

"""
