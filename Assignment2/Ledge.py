
class Ledge:

    def __init__(self, inital_board):
        self.initial_board = inital_board
        self.board = inital_board

    def do_move(self, move):
        if self.legal_move(move):
            coin = self.board[move[0]]
            if move[0] == 0:
                self.board[0] = 0
                return coin, True
            self.board[move[0]] = 0
            self.board[move[1]] = coin

            return coin, False

        return -1, False

    def legal_move(self, move):
        pass
