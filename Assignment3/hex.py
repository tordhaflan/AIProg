import networkx as nx
import matplotlib.pyplot as plt


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

    def set_neighbours(self):
        """ Sets the neighbours of a peg
        """
        for i in range(self.layers):
            for j in range(self.layers):
                if self.board[i][j] is not None:
                    n = find_neighbourhood(i, j, self.layers)
                    self.board[i][j].set_neighbours(n)

    def reset_board(self):
        """ To initialize the open cells in the board

        :param open_cells: list of tuples, coordinates of open cells
        """
        for r in range(self.layers):
            for c in range(self.layers):
                self.board[r][c].filled = 0

    def do_move(self, row, col, player):
        self.board[row][col].filled = player
        return self.get_board(player)

    def get_board(self, player):
        state = []
        #state.append(player % 2 + 1)
        for r in range(self.layers):
            for c in range(self.layers):
                state.append(self.board[r][c].filled)

        return state

    #TODO
    # Make this!
    # Add final path attribute (a list) to Hex object
    # Burde sørge for at vi ikke kaller på denne for ofte.
    def is_win(self, player):
        visited = [[False for r in range(self.layers)] for c in range(self.layers)]
        if player == 2:
            top = [(0, i) for i in range(self.layers)]
            bottom = [(self.layers-1, i) for i in range(self.layers)]
        else:
            top = [(i, 0) for i in range(self.layers)]
            bottom = [(i, self.layers - 1) for i in range(self.layers)]

        for r, c in top:
            for r2, c2 in bottom:
                if self.board[r][c].filled == player and self.board[r2][c2].filled == player:
                    queue = []
                    path = []

                    queue.append((r, c))
                    path.append((r, c))
                    visited[r][c] = True

                    while queue:
                        n = queue.pop(0)

                        if n[0] == r2 and n[1] == c2:
                            self.final_path = path
                            print(self.final_path)
                            return True

                        for i, j in self.board[n[0]][n[1]].neighbours:
                            if visited[i][j] is False and self.board[i][j].filled == player \
                                    and self.board[i][j].coordinates not in top:
                                queue.append((i, j))
                                path.append((i, j))
                                visited[i][j] = True


        return False


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

def draw_board(board):
    """ Just in case we are asked to display a board on the demo.

    :param board: the Board-object
    :return: Displays a board
    """
    G = nx.Graph()
    color_map = {}
    border_color = {}
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
                    G.add_edge(peg.pegNumber, board[x][y].pegNumber)
    pos = nx.get_node_attributes(G, 'pos')
    color, border = sort_color(pos, color_map, border_color)
    nx.draw_networkx(G, pos, node_color=color, edgecolors=border, with_labels=False)
    plt.show()

h = Hex(5)

h.do_move(0,0,1)
h.do_move(0,1,1)
h.do_move(1,2,1)
h.do_move(0,2,1)
h.do_move(1,0,1)
h.do_move(0,3,1)
h.do_move(0,4,1)


draw_board(h.board)
print(h.is_win(1))
h.reset_board()

#draw_board(h.board)
