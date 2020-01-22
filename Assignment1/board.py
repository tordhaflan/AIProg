import networkx as nx
import matplotlib.pyplot as plt
from Assignment1.peg import Peg


class Board(object):

    def __init__(self, layers=3, diamond=False):
        self.layers = layers
        self.diamond = diamond

        self.board = make_graph(self.layers, self.diamond)
        self.set_neighbours()

    def set_neighbours(self):
        for i in range(self.layers):
            for j in range(self.layers):
                if self.board[i][j] is not None:
                    n = self.find_neighbourhood(i, j)
                    self.board[i][j].set_neighbours(n)

    def find_neighbourhood(self, row, col):
        neighbourhood = []
        for i in range(6):
            if check_boundary(row - 1, col, self.layers, self.diamond) and i == 0:
                neighbourhood.append((row - 1, col))
            elif check_boundary(row + 1, col, self.layers, self.diamond) and i == 1:
                neighbourhood.append((row + 1, col))
            elif check_boundary(row, col - 1, self.layers, self.diamond) and i == 2:
                neighbourhood.append((row, col - 1))
            elif check_boundary(row, col + 1, self.layers, self.diamond) and i == 3:
                neighbourhood.append((row, col + 1))
            elif self.diamond:
                if check_boundary(row - 1, col + 1, self.layers, self.diamond) and i == 4:
                    neighbourhood.append((row - 1, col + 1))
                elif check_boundary(row + 1, col - 1, self.layers, self.diamond) and i == 4:
                    neighbourhood.append((row + 1, col - 1))
            else:
                if check_boundary(row + 1, col + 1, self.layers, self.diamond) and i == 5:
                    neighbourhood.append((row + 1, col + 1))
                elif check_boundary(row - 1, col - 1, self.layers, self.diamond) and i == 5:
                    neighbourhood.append((row - 1, col - 1))

        return neighbourhood


def make_graph(layers, diamond):
    if diamond:
        row = 2 * layers - 1
    else:
        row = layers

    graph = [[None for x in range(layers)] for y in range(layers)]
    n = 1
    for i in range(row):
        if diamond:
            if i < layers:
                graph, n = make_upper_triangle(graph, layers, row, i, n)
            else:
                graph, n = make_lower_triangle(graph, layers, row, i, n)
        else:
            graph, n = make_triangle(graph, layers, row, i, n)

    return graph


def make_upper_triangle(graph, layers, row, i, n):
    k = 0
    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        graph[i - j][j] = Peg(k, row - i, n)
        n += 1
        k += 2
    return graph, n


def make_lower_triangle(graph, layers, row, i, n):
    k = 0
    for j in range(i - layers + 1, 0, -1):
        k += 1
    for j in range(row - i):
        graph[layers - j - 1][i - layers + j + 1] = Peg(k, row - i, n)
        n += 1
        k += 2
    return graph, n


def make_triangle(graph, layers, row, i, n):
    k = 0
    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        graph[i][j] = Peg(k, row - i, n)
        n += 1
        k += 2
    return graph, n


def draw_board(board):
    G = nx.Graph()
    for b in board.board:
        for i in range(len(b)):
            peg = b[i]
            if peg is not None:
                G.add_node(peg.pegNumber, pos=peg.coordinates)
                for x,y in peg.neighbours:
                    G.add_edge(peg.pegNumber, board.board[x][y].pegNumber)
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx(G, pos)
    plt.show()


def check_boundary(row, col, layers, diamond):
    if row < 0 or col < 0:
        return False
    elif row >= layers or col >= layers:
        return False
    elif not diamond and col > row:
        return False
    return True


B = Board(4, True)

draw_board(B)
