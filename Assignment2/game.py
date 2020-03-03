import copy
import random

from Assignment2.Nim import Nim
from Assignment2.Ledge import Ledge
from Assignment2.read_initialization import read_parameters_file
from Assignment2.MCTS import MCTS


class Game:

    def __init__(self, params=read_parameters_file()):
        self.game_type = params[0]
        self.batches = params[1]
        self.episodes = params[2]
        self.player = params[3]
        self.verbose = params[-1]

        if self.game_type == "Nim":
            self.game = Nim(params[4], params[5])
        else:
            self.game = Ledge(params[4])

        self.mcts = MCTS(self)

    def run(self):
        for i in range(self.batches):
            print(self.game.print(self.game.state, None))

            while not self.game.game_over():
                self.mcts.simulate(self.episodes)
                action = self.mcts.get_action(self.game.state)
                string = self.game.print(self.game.state, action)
                self.game.state = self.game.do_move(self.game.state, action)
                if self.verbose:
                    print("P" + str(self.player) + string + str(self.game.state))

                self.mcts.reset_values()
                self.player = (self.player % 2) + 1

            print("Player " + str(self.player % 2 + 1) + " wins")

            self.game.reset_game()

    def get_initial_state(self):
        return self.game.get_initial_state()

    def get_child_action_pair(self, state):
        states = []
        actions = self.game.child_actions(state)

        for a in actions:
            new_state = copy.deepcopy(state)
            states.append((self.game.do_move(new_state, a), a))
        return states

    def get_actions(self, state):
        return self.game.child_actions(state)

    def get_random_action(self, state):
        actions = self.game.child_actions(state)
        return actions[random.randint(0, len(actions)-1)]

    def is_win(self, state):
        return self.game.game_over(state)

    def do_action(self, state, action):
        state = self.game.do_move(state, action)
        return state

    # Tenkte det er greit at man bare kan kalle på game-objectet sin state.
    def get_state(self):
        return self.game.get_state()


g = Game()
print(g.get_state())
g.do_action((4,3))
print(g.get_state())
g.do_action((3,2))
print(g.get_state())
