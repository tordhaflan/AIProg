import copy


class Nim:

    def __init__(self, heap_size, max_action):
        self.heap_size = heap_size
        self.max_action = max_action
        self.state = heap_size
        self.player = 1

    def do_move(self, state, move):
        if self.legal_move(state, move):
            state -= move
        return state

    def legal_move(self, state, move):
        return True if move <= state and move <= self.max_action else False

    def game_over(self, state):
        return True if state == 0 else False

    def child_actions(self, state):
        if state > self.max_action:
            return [i for i in range(self.max_action)]
        else:
            return [i for i in range(state)]

    def print(self, state, move):
        if move is None:
            return "Start Pil: " + str(state) + " stones."
        else:
            return " selects " + str(move) + "stones: Remaining stones = "


    def reset_game(self):
        self.state = copy.deepcopy(self.heap_size)

    def set_game(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_initial_state(self):
        return self.heap_size

    def play_game(self, state):
        sign = 1
        """
        Just to test the game, will not use it in the MCTS simulation
        """
        print("Welcome to a simple game of Nim :) \n")

        while state > 0:
            heap = state
            print("----------------------------------\n")
            print("Player {}s turn\n".format(self.player))
            print("Pieces on the heap: ", state, "\n")
            move = int(input("How many pieces du you want to remove? "))

            state = self.do_move(state, move)
            if move > state + move:
                print("\nYou cant remove more pices then is left on the heap! \n")
            elif heap == state:
                print("\nIllegal move, the move has to be <=", self.max_action, ", try another move!\n")
            else:
                self.player += sign
                sign = -1 * sign

        self.player += sign * self.player
        print("\nCongratulation player {}, you won!".format(self.player))
