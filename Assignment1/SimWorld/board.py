import networkx as nx
import matplotlib.pyplot as plt
from Assignment1.SimWorld.peg import Peg


class Board(object):
    def __init__(self, layers=3, diamond=False):
        """ Initialize  Board-object

        :param layers: Size of the board
        :param diamond: Type of board
        """
        self.layers = layers
        self.diamond = diamond
        self.board = make_graph(self.layers, self.diamond)
        self.set_neighbours()

    def set_neighbours(self):
        """ Sets the neighbours of a peg
        """
        for i in range(self.layers):
            for j in range(self.layers):
                if self.board[i][j] is not None:
                    n = self.find_neighbourhood(i, j)
                    self.board[i][j].set_neighbours(n)

    def find_neighbourhood(self, row, col):
        """ Finds all the neighbours of a peg that set_neighbours then sets.

        :param row: int, row coordinate
        :param col: int, col coordinate
        :return: list of tuples, all neighbouring coordinates that are legal
        """
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
                elif check_boundary(row + 1, col - 1, self.layers, self.diamond) and i == 5:
                    neighbourhood.append((row + 1, col - 1))
            else:
                if check_boundary(row + 1, col + 1, self.layers, self.diamond) and i == 4:
                    neighbourhood.append((row + 1, col + 1))
                elif check_boundary(row - 1, col - 1, self.layers, self.diamond) and i == 5:
                    neighbourhood.append((row - 1, col - 1))

        return neighbourhood

    def set_open_cells(self, open_cells):
        """ To initialize the open cells in the board

        :param open_cells: list of tuples, coordinates of open cells
        """
        for r, c in open_cells:
            self.board[r][c].filled = False


def make_graph(layers, diamond):
    """ To make the board itself.

    :param layers: int, Size of the board
    :param diamond: boolean, Type of board
    :return: A list of Peg-objects
    """
    if diamond:
        row = 2 * layers - 1
    else:
        row = layers

    graph = [[None for x in range(layers)] for y in range(layers)]
    n = 1
    for i in range(row):
        if diamond:
            if i < layers:
                graph, n = make_upper_diamond(graph, layers, row, i, n)
            else:
                graph, n = make_lower_diamond(graph, layers, row, i, n)
        else:
            graph, n = make_triangle(graph, layers, row, i, n)

    return graph


def make_upper_diamond(graph, layers, row, i, n):
    """ Makes the upper half of a diamond. Takes "empty cells" into account.

    :param graph: The list of Pegs
    :param layers: Size
    :param row: What row currently being made
    :param i: Column parameter
    :param n: Peg number
    :return: The updated graph and peg number
    """
    k = 0
    col = 0
    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        graph[i - j][j] = Peg(k, row - i - 1, i - col, col, n)
        n += 1
        k += 2
        col += 1
    return graph, n


def make_lower_diamond(graph, layers, row, i, n):
    """ Makes the lower half of a diamond. Takes "empty cells" into account.

    :param graph: The list of Pegs
    :param layers: Size
    :param row: What row currently being made
    :param i: Column parameter
    :param n: Peg number
    :return: The updated graph and peg number
    """
    k = 0
    col = 1
    for j in range(i - layers + 1, 0, -1):
        k += 1
    for j in range(row - i):
        graph[layers - j - 1][i - layers + j + 1] = Peg(k, row - i - 1, layers - col, i - layers + col, n)
        n += 1
        k += 2
        col += 1
    return graph, n


def make_triangle(graph, layers, row, i, n):
    """Makes a triangle. Takes "empty cells" into account.

    :param graph: The list of Pegs
    :param layers: Size
    :param row: What row currently being made
    :param i: Column parameter
    :param n: Peg number
    :return: The updated graph and peg number
    """
    k = 0
    col = 0
    for j in range(layers - i - 1):
        k += 1
    for j in range(i + 1):
        graph[i][j] = Peg(k, row - i - 1, i, col, n)
        n += 1
        k += 2
        col += 1
    return graph, n


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


def check_boundary(row, col, layers, diamond):
    """ Checks if a tuple of coordinates is within the boundaries of the board.

    :param row: row coordinate
    :param col: col coordinate
    :param layers: size
    :param diamond: board-shape
    :return: True if the coordinates is within the boundaries of the board
    """
    if row < 0 or col < 0:
        return False
    elif row >= layers or col >= layers:
        return False
    elif not diamond and col > row:
        return False
    return True


def draw_board(board):
    """ Just in case we are asked to display a board on the demo.

    :param board: the Board-object
    :return: Displays a board
    """
    G = nx.Graph()
    color_map = {}
    border_color = {}
    for b in board.board:
        for i in range(len(b)):
            peg = b[i]
            if peg is not None:
                G.add_node(peg.pegNumber, pos=peg.drawing_coordinates)
                if peg.filled:
                    color_map[peg.pegNumber] = 'darkblue'
                    border_color[peg.pegNumber] = 'darkblue'
                else:
                    color_map[peg.pegNumber] = 'white'
                    border_color[peg.pegNumber] = 'grey'

                for x, y in peg.neighbours:
                    G.add_edge(peg.pegNumber, board.board[x][y].pegNumber)
    pos = nx.get_node_attributes(G, 'pos')
    color, border = sort_color(pos, color_map, border_color)
    nx.draw_networkx(G, pos, node_color=color, edgecolors=border, with_labels=False)
    plt.show()
