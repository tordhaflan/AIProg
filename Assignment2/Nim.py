import copy


class Nim:

    def __init__(self, heap_size, max_action):
        """ Init Nim-object

        :param heap_size: int, start heap size
        :param max_action: int, max amount possible to remove each turn
        """
        self.heap_size = heap_size
        self.max_action = max_action
        self.state = heap_size
        self.player = 1

    def do_move(self, state, move):
        """ Perform a move

        :param state: int, current heap size
        :param move: int, amount to remove in a move
        :return: int, updated heap size
        """
        if self.legal_move(state, move):
            state -= move
        return state

    def legal_move(self, state, move):
        """ Check if a move is legal

        :param state: int, current heap size
        :param move: int, amount to remove in a move
        :return: True if legal move
        """
        return True if move <= state and move <= self.max_action and move > 0 else False

    def game_over(self, state):
        """ Check if a game is finished

        :param state: int, current heap size
        :return: True if game over
        """
        return True if state == 0 else False

    def child_actions(self, state):
        """ produces a list of possible actions from current state

        :param state: int, current heap size
        :return: A list of moves
        """
        if state > self.max_action:
            return [i for i in range(1, self.max_action + 1)]
        else:
            return [i for i in range(1, state + 1)]

    def print(self, state, move):
        """ Produces the string to print in verbose mode

         :param state: int, current heap size
         :param move: int, amount to remove in a move
         :return: string to print
         """
        if move is None:
            return "Start Pile: " + str(state) + " stones"
        else:
            return " selects " + str(move) + " stones: Remaining stones = "

    def reset_game(self):
        """ Resets the state to the initial board
        """
        self.state = copy.deepcopy(self.heap_size)

    def get_initial_state(self):
        """ Get the start board

        :return: int, initial state
        """
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
