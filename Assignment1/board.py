import networkx as nx
import matplotlib.pyplot as plt
from Assignment1.peg import Peg


class Board(object):

    def __init__(self, layers=3, diamond=False):
        self.layers = layers
        self.diamond = diamond
        self.board = self.initialize_board()

    def initialize_board(self):
        graph = make_graph(self.layers, self.diamond)
        board = []
        if self.diamond:
            for i in range(self.layers):
                row = []
                for j in range(self.layers):
                    x = graph[i + j * self.layers][0]
                    y = graph[i + j * self.layers][1]
                    number = graph[i + j * self.layers][2]
                    row.append(Peg(x, y, number))
                board.append(row)
        else:
            print("Wait and see")

        return board


def make_graph(layers, diamond):
    if diamond:
        row = 2 * layers - 1
    else:
        row = layers

    graph = []
    n = 1
    for i in range(row):
        if diamond:
            if i < layers:
                graph, n = make_upper_triangle(graph, layers, row, i, n)
            else:
                graph, n = make_lower_triangle(graph, layers, row, i, n)

        else:
            graph, n = make_upper_triangle(graph, layers, row, i, n)

    return graph


def make_upper_triangle(graph, layers, row, i, n):
    k = 0
    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        graph.append((k, row - i, n))
        n += 1
        k += 2
    return graph, n


def make_lower_triangle(graph, layers, row, i, n):
    k = 0
    for j in range(i - layers + 1, 0, -1):
        k += 1
    for j in range(row - i):
        graph.append((k, row - i, n))
        n += 1
        k += 2
    return graph, n


def draw_board(board):
    G = nx.Graph()
    n = 1
    for b in board.board:
        for i in range(len(b)):
            peg = b[i]
            G.add_node(peg.pegNumber, pos=peg.coordinates)
            n += 1
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx(G, pos)
    plt.show()


B = Board(4, True)

draw_board(B)
