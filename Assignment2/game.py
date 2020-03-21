import copy
import random

from Assignment2.Nim import Nim
from Assignment2.Ledge import Ledge
from Assignment2.read_initialization import read_parameters_file
from Assignment2.MCTS import MCTS


class Game:

    def __init__(self, params=read_parameters_file()):
        """ Initialize game manager

        :param params: For Nim - [Game name, batch size, number of simulations, player to start, heap size,
                        max number of pices to remove, verbose]
                    For Ledge - [Game name, batch size, number of simulations, player to start, initial board, verbose]
        """
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
        """ Running the simulation G times.
        """
        for i in range(self.batches):

            player = copy.deepcopy(self.initial_player)
            if i % 10 == 0:
                print(i)
            if self.verbose:
                print(self.game.print(self.game.state, None))

            while not self.game.game_over(self.game.state):
                self.mcts.reset(copy.deepcopy(self.game.state))
                self.mcts.simulate(self.episodes)
                action = self.mcts.get_action()
                string = self.game.print(self.game.state, action)
                self.game.state = self.game.do_move(self.game.state, action)
                if self.verbose:
                    print("P" + str(player) + string + str(self.game.state))

                player = (player % 2) + 1

            if self.verbose:
                print("Player " + str(player % 2 + 1) + " wins \n")

            self.winner.append(player % 2 + 1)
            self.game.reset_game()
            self.mcts.reset(self.game.state)

        print("Player 1 wins: ", self.winner.count(1))
        print("Player 2 wins: ", self.winner.count(2))
        percent = self.winner.count(1)/(self.winner.count(1)+self.winner.count(2))*100
        if self.winner.count(1) >= self.winner.count(2):
            print("Player 1 wins " + str(int(percent)) + " percent of the games \n")
        else:
            print("Player 2 wins " + str(100 - int(percent)) + " percent of the games \n")

    def get_initial_state(self):
        """ Gets initial board from game-attribute

        :return: int or list, board
        """
        return self.game.get_initial_state()

    def get_child_action_pair(self, state):
        """ Finds all children of a state and the action leading to each child.

        :param state: state to find children from
        :return: list of tuples, (state, action)
        """
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
        """ Produces a list of possible actions from a state

        :param state: state to find actions from
        :return: list of actions
        """
        return self.game.child_actions(state)

    def get_random_action(self, state):
        """ Produces a random action of possible actions from a state

        :param state: state to find action from
        :return: 1 action
        """
        actions = self.game.child_actions(state)
        return actions[random.randint(0, len(actions)-1)]

    def is_win(self, state):
        """ Checks if a game is finished.

        :param state: last state to check if is final
        :return:
        """
        return self.game.game_over(state)

    def do_action(self, state, action):
        """ Perform an action in game

        :param state: state to perform action from
        :param action: action to perform
        :return: updated state after action is performed
        """
        state = self.game.do_move(state, action)
        return state


g = Game()
g.run()
