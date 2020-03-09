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
        if params[3] == 3:
            self.initial_player = random.randint(1, 3)
        else:
            self.initial_player = params[3]
        self.verbose = params[-1]
        self.winner = []

        if self.game_type == "Nim":
            self.game = Nim(params[4], params[5])
        else:
            self.game = Ledge(params[4])
            self.copy = self.game

        self.mcts = MCTS(self, self.game.state)

    def run(self):
        for i in range(self.batches):

            player = copy.deepcopy(self.initial_player)
            if i % 10 == 0:
                print(i)
            if self.verbose:
                print(self.game.print(self.game.state, None))

            while not self.game.game_over(self.game.state):
                self.mcts.simulate(self.episodes)
                action = self.mcts.get_action()
                string = self.game.print(self.game.state, action)
                self.game.state = self.game.do_move(self.game.state, action)
                if self.verbose:
                    print("P" + str(player) + string + str(self.game.state))

                player = (player % 2) + 1

                self.mcts.reset(copy.deepcopy(self.game.state))

            if self.verbose:
                print("Player " + str(player % 2 + 1) + " wins")

            self.winner.append(player % 2 + 1)
            self.game.reset_game()
            self.mcts.reset(self.game.state)

        print("Player 1 wins: ", self.winner.count(1))
        print("Player 2 wins: ", self.winner.count(2))

    def get_initial_state(self):
        return self.game.get_initial_state()

    def get_child_action_pair(self, state):
        if self.game.game_over(state):
            return []
        else:
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
g.run()
