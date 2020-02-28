import random

from Assignment2.Nim import Nim
from Assignment2.Ledge import Ledge
from Assignment2.read_initialization import read_parameters_file


class Game:

    def __init__(self, params=read_parameters_file()):
        self.game_type = params[0]
        self.batches = params[1]
        self.simulations = params[2]
        self.player = params[3]
        self.verbose = params[-1]

        if self.game_type == "Nim":
            self.game = Nim(params[4], params[5])
        else:
            self.game = Ledge(params[4])

    def get_initial_state(self):
        return self.game.get_initial_state()

    def get_child_states(self):
        states = []
        actions = self.game.child_actions()

        for a in actions:
            game = self.game.get_state()
            states.append(self.game.do_move(a))
            self.game.set_game(game)
        return states

    def get_actions(self):
        return self.game.child_actions()

    def get_random_action(self):
        actions = self.game.child_actions()
        return actions[random.randint(0, len(actions)-1)]

    def is_win(self):
        check = self.game.game_over()
        if check:
            self.game.reset_game()

        return check

    def do_action(self, action):
        self.game.do_move(action)

    # Tenkte det er greit at man bare kan kalle på game-objectet sin state.
    def get_state(self):
        return self.game.get_state()


g = Game()

print(g.get_state())

g.do_action((4,3))
print(g.get_state())
g.do_action((3,2))
print(g.get_state())
