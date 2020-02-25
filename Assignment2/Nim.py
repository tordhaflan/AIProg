import copy


class Nim:

    def __init__(self, heap_size, max_action):
        self.heap_size = heap_size
        self.max_action = max_action
        self.heap = heap_size
        self.player = 1

    def do_move(self, move):
        if self.legal_move(move):
            self.heap -= move
        return self.heap

    def legal_move(self, move):
        return True if move <= self.heap and move <= self.max_action else False

    def game_over(self):
        return True if self.heap == 0 else False

    def child_actions(self):
        if self.heap > self.max_action:
            return [i for i in range(self.max_action)]
        else:
            return [i for i in range(self.heap)]

    def reset_game(self):
        self.heap = copy.deepcopy(self.heap_size)

    def set_game(self, state):
        self.heap = state

    def get_state(self):
        return self.heap

    def play_game(self):
        sign = 1
        """
        Just to test the game, will not use it in the MCTS simulation
        """
        print("Welcome to a simple game of Nim :) \n")

        while self.heap > 0:
            heap = self.heap
            print("----------------------------------\n")
            print("Player {}s turn\n".format(self.player))
            print("Pieces on the heap: ", self.heap, "\n")
            move = int(input("How many pieces du you want to remove? "))

            self.do_move(move)
            if move > self.heap + move:
                print("\nYou cant remove more pices then is left on the heap! \n")
            elif heap == self.heap:
                print("\nIllegal move, the move has to be <=", self.max_action, ", try another move!\n")
            else:
                self.player += sign
                sign = -1 * sign

        self.player += sign * self.player
        print("\nCongratulation player {}, you won!".format(self.player))


#n = Nim(40, 7)

#n.play_game()
