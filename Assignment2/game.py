from Assignment2.Nim import Nim
from Assignment2.Ledge import Ledge
from Assignment2.read_initialization import *
import copy


class Game:

    def __init__(self, params):
        self.game_type = params[0]
        self.batches = params[1]
        self.simulations = params[2]
        self.player = params[3]
        self.verbose = params[-1]

        if self.game_type == "Nim":
            self.game = Nim(params[4], params[5])
        else:
            self.game = Ledge(params[4])

    #TODO
    # Denne endrer board for hver gang den henter ut states. Hvis man kaller
    # på den mange ganger blir board til slutt tomt
    def get_child_states(self):
        states = []
        actions = self.game.child_actions()


        for a in actions:
            game = copy.deepcopy(self.game.get_state())
            states.append((self.game.do_move(a), a))
            self.game.set_game(game)


        return states

    def game_over(self):
        return self.game.game_over()

    def do_action(self, action):
        self.game.do_move(action)


# if __name__ == '__main__':
#    game = Game(read_parameters_file())


