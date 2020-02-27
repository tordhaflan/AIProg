import random
import copy


class Ledge:

    def __init__(self, initial_board):

        if len(initial_board) == 0:
            size = random.randint(0, 20)
            self.initial_board = init_board(size, random.randint(0, size-1))
        else:
            self.initial_board = initial_board
        self.board = initial_board

    def do_move(self, move):
        if self.legal_move(move):
            coin = self.board[move[0]]
            if move[0] == 0:
                self.board[0] = 0
                return self.board
            self.board[move[0]] = 0
            self.board[move[1]] = coin

            return self.board

        return self.board

    def legal_move(self, move):
        if move[0] == 0 and move[1] == 0:
            return True if self.board[0] > 0 else False
        if move[0] > move[1] and self.board[move[0]] > 0:
            for i in range(move[1], move[0]):
                if not self.board[i] == 0:
                    return False
            return True
        return False

    def game_over(self):
        return True if 2 not in self.board else False

    def child_actions(self):
        actions = []
        if self.board[0] > 0:
            actions.append((0, 0))

        c = 0
        for i in range(len(self.board) - 1, -1, -1):
            if self.board[i] > 0:
                c = i
            elif c > 0 and self.board[i] == 0:
                actions.append((c, i))
        return actions

    def reset_game(self):
        self.board = copy.deepcopy(self.initial_board)

    def set_game(self, board):
        self.board = board

    def get_state(self):
        return self.board

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
