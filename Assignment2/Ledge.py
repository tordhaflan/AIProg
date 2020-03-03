import random
import copy


class Ledge:

    def __init__(self, initial_board):

        if len(initial_board) == 0:
            size = random.randint(0, 20)
            self.initial_board = init_board(size, random.randint(0, size-1))
        else:
            self.initial_board = initial_board
        self.state = initial_board

    # Et move er på formen (from possition, to possition)
    def do_move(self, state, move):
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
        if move[0] == 0 and move[1] == 0:
            return True if state[0] > 0 else False
        if move[0] > move[1] and state[move[0]] > 0:
            for i in range(move[1], move[0]):
                if not state[i] == 0:
                    return False
            return True
        return False

    def game_over(self, state):
        return True if 2 not in state else False

    def child_actions(self, state):
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
        self.state = copy.deepcopy(self.initial_board)

    def set_game(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_initial_state(self):
        return self.initial_board


def init_board(length, copper):

    board = [0 for i in range(0, length)]
    gold = random.randint(0, length - 1)
    board[gold] = 2

    if (copper >= 0) and (copper < length):
        coppers = [1 for i in range(0, copper)]
        while len(coppers) > 0:
            i = random.randint(0, length - 1)
            if board[i] == 0:
                board[i] = 1
                coppers.pop()

    return board
