import copy
import operator
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Assignment1.SimWorld.board import Board, check_boundary, sort_color


class Player:

    # Må skrives om slik at den tar inn parametere og lager et board objekt selv
    # Init Player-object
    def __init__(self, game=Board, open_cells=[]):

        # Kopi av inital game for å bruke til å vise fram
        self.initial_game = copy.deepcopy(game)
        self.game = game
        self.move = legal_moves(self.game.diamond)
        self.counter = 0
        self.pegs_left = 0

        self.game.set_open_cells(open_cells)
        self.initial_game.set_open_cells(open_cells)  # endres når vi initialiserer player objektet med et board -> sendes da som en inputverdi

    # Bruker binær tuppelliste i alle utregninger.
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

    # Hente alle lovlige moves
    # Tuple map for å legge sammen peg og jump/end
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

    # Selve utførelsen av et move
    def do_move(self, move):
        start, jump, goal = move[0], move[1], move[2]

        self.game.board[start[0]][start[1]].filled = False
        self.game.board[jump[0]][jump[1]].filled = False
        self.game.board[goal[0]][goal[1]].filled = True

        return self.get_binary_board()

    # Sjekke om det er lovlige moves igjen
    def game_over(self):
        if more_moves_available(self.game):
            return False
        return True

    # Gir 1 i reward dersom game won, ellers negativ pegs_left/antall pegs
    def get_reward(self):
        self.pegs_left = 0
        for row in self.game.board:
            for element in row:
                if element is not None and element.filled:
                    self.pegs_left += 1
        self.game = copy.deepcopy(self.initial_game)
        # TODO
        # endre self.initial_game.layers ** 2 til antall pegs totalt, if triangle osv.
        return (1,self.pegs_left) if self.pegs_left == 1 else (-self.pegs_left / self.initial_game.layers ** 2, self.pegs_left)  # kanskje skrive om else for triangel

    # Selve funksjonen som animerer spillet
    def update(self, num, G, actions, ax1, ax2, fig, pegs_left):
        # resetter plottet
        if self.counter < len(actions) + 2:
            ax1.clear()
        color_map = {}
        border_color = {}

        # Viser kun startrettet første gang og nest siste gang
        # Fargelegger pegs
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

            # Tilbakemelding på spill på nest siste plot
            if self.pegs_left == 1 and self.counter == len(actions) + 1:
                ax1.set_title("Congratulation - The RL made it")
            elif self.counter == len(actions) + 1:
                ax1.set_title("The RL failed")

        # For alle andre ganger, bortsett fra siste, selve spillanimasjonen
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

        # Plotting av siste spillbrett, halvere størrelse og vise plot av pegs_left
        if self.counter == len(actions) + 2:
            ax1.change_geometry(1, 2, 1)
            ax1.set_title("Final board")
            x = np.arange(len(pegs_left))
            ax2.set_title("Statistics over pegs left")
            ax2.set_xlabel("Episodes")
            ax2.set_ylabel("Pegs left")
            ax2.plot(x, pegs_left)
            ax2.set_visible(True)

        # Utfører selve endringer av grafen, sort_color for å endre peg-sortering til den nx liker
        # Den sorterte på en annen måte enn vi la de inn. Noe flipping av strukturen.
        else:
            pos = nx.get_node_attributes(G, 'pos')
            color, border = sort_color(pos, color_map, border_color)
            nx.draw_networkx(G, pos=pos, node_color=color, edgecolors=border, with_labels=False, ax=ax1)
            self.counter += 1
            fig.canvas.set_window_title('Peg Solitaire - RL')

    # Animasjon av spillet
    def show_game(self, actions, pegs_left):
        # Lager figuren og de 2 plotsene som kommer til slutt
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(13, 11))
        # Sjuler plot
        ax2.set_visible(False)
        ax1.change_geometry(1, 1, 1)

        # Bygger strukturen til spillbrettet/grafen
        G = nx.Graph()
        for b in self.game.board:
            for i in range(len(b)):
                peg = b[i]
                if peg is not None:
                    G.add_node(peg.pegNumber, pos=peg.drawing_coordinates)
                    for x, y in peg.neighbours:
                        G.add_edge(peg.pegNumber, self.game.board[x][y].pegNumber)

        # Animasjonen av spillet
        ani = FuncAnimation(fig, self.update, frames=(len(actions) + 2), fargs=(G, actions, ax1, ax2, fig, pegs_left),
                            interval=2000, repeat=False)
        plt.show()


# Koordinater til naboer og naboer av naboer av en peg
def legal_moves(diamond):
    moves = [[(-1, 0), (-2, 0)], [(1, 0), (2, 0)], [(0, -1), (0, -2)], [(0, 1), (0, 2)]]

    if diamond:
        moves.append([(-1, 1), (-2, 2)])
        moves.append([(1, -1), (2, -2)])
    else:
        moves.append([(-1, -1), (-2, -2)])
        moves.append([(1, 1), (2, 2)])

    return moves


# Sjekke om et move er lovlig
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


# Sjekke om et punkt har en peg som er filled
def is_filled(game, coordinates):
    if game.board[coordinates[0]][coordinates[1]].filled:
        return True

    return False


# Sjekke om de ligger på linje
def is_on_line(start, jump, end):
    delta_row = jump[0] - start[0]
    delta_column = jump[1] - start[1]
    if end[0] == jump[0] + delta_row and end[1] == jump[1] + delta_column:
        return True

    return False


# Sjekke om det går an å gjøre flere moves
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
