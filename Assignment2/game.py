from Assignment2.Nim import Nim
from Assignment2.Ledge import Ledge
import copy


class Game:

    def __init__(self, params, verbose=False):
        self.batches = params[1]
        self.simulations = params[2]
        self.player = params[3]
        self.verbose = params[-1]

        if params[0] == "Nim":
            self.game = Nim(params[4], params[5])
        else:
            self.game = Ledge(params[4])

    def get_child_states(self):
        states = []
        actions = self.game.child_actions()

        for a in actions:
            game = copy.deepcopy(self.game)
            states.append((self.game.do_move(a), a))
            self.game.set_game(game)

        return states

    def game_over(self):
        return self.game.game_over()

    def do_action(self, action):
        self.game.do_move(action)