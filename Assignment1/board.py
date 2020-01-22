import networkx as nx
import matplotlib.pyplot as plt
from Assignment1.peg import Peg


class Board(object):

    def __init__(self, layers=3, diamond=False):
        self.layers = layers
        self.diamond = diamond
        self.board = make_graph(self.layers, self.diamond)


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
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx(G, pos)
    plt.show()


B = Board(4)

draw_board(B)

