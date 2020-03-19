import random
import copy


class Ledge:

    def __init__(self, initial_board):
        """ Initialize Ledge-object

        :param initial_board: list, initial board
        """

        if len(initial_board) == 0:
            size = random.randint(0, 20)
            self.initial_board = init_board(size, random.randint(0, size-1))
        else:
            self.initial_board = initial_board
        self.state = copy.deepcopy(self.initial_board)

    def do_move(self, state, move):
        """ Performing a move (from pos, to pos)

        :param state: list, current board
        :param move: tuple, (from pos, to pos)
        :return: state: list, board after move
        """
        if self.legal_move(state, move):
            coin = state[move[0]]
            if move[0] == 0:
                state[0] = 0
                return state
            state[move[0]] = 0
            state[move[1]] = coin

            return state

        return state

    def legal_move(self, state, move):
        """ Checks if a move is legal.

        :param state: list, current board
        :param move: tuple, (from pos, to pos)
        :return: True if move is legal
        """
        if move[0] == 0 and move[1] == 0:
            return True if state[0] > 0 else False
        if move[0] > move[1] and state[move[0]] > 0:
            for i in range(move[1], move[0]):
                if not state[i] == 0:
                    return False
            return True

        return False

    def game_over(self, state):
        """ Checks if a game of Ledge is finished.

        :param state: list, current board
        :return: True if game over
        """
        return True if 2 not in state else False

    def child_actions(self, state):
        """ produces a list of possible actions from current state

        :param state: list, current board
        :return: A list of moves
        """
        actions = []
        if state[0] > 0:
            actions.append((0, 0))

        c = 0
        for i in range(len(state) - 1, -1, -1):
            if state[i] > 0:
                c = i
            elif c > 0 and state[i] == 0:
                actions.append((c, i))

        return actions

    def print(self, state, move):
        """ Produces the string to print in verbose mode

        :param state: list, current board
        :param move: tuple, (from pos, to pos)
        :return: string to print
        """
        if move is None:
            return "Start Board: " + str(self.initial_board)
        elif move[0] == 0:
            return " picks up copper " if state[0] == 1 else " picks up gold "
        else:
            if state[move[0]] == 1:
                return " moves copper from cell " + str(move[0]) + " to " + str(move[1]) + ": "
            else:
                return " moves gold from cell " + str(move[0]) + " to " + str(move[1]) + ": "

    def reset_game(self):
        """ Resets the state to the initial board
        """
        self.state = copy.deepcopy(self.initial_board)

    def get_initial_state(self):
        """ Get the start board

        :return: list, initial state
        """
        return self.initial_board


def init_board(length, copper):
    """ Help function to create a Ledge board from random parameters.

    :param length: int, Amount of positions on board
    :param copper: int, number of 1's
    :return: list, the board
    """

    board = [0 in range(0, length)]
    gold = random.randint(0, length - 1)
    board[gold] = 2

    if (copper >= 0) and (copper < length):
        coppers = [1 in range(0, copper)]
        while len(coppers) > 0:
            i = random.randint(0, length - 1)
            if board[i] == 0:
                board[i] = 1
                coppers.pop()
    return board
