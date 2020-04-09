import copy
import random
from tqdm import tqdm

from Assignment3.hex import Hex, draw_board
from Assignment3.read_file import read_file
from Assignment3.MCTS_ANET import MCTS_ANET, distibution_to_action
from Assignment3.ANET import ANET


class Game:

    def __init__(self, params=read_file()):
        """ Initialize game manager

        :param params: For Nim - [Game name, batch size, number of simulations, player to start, heap size,
                        max number of pices to remove, verbose]
                    For Ledge - [Game name, batch size, number of simulations, player to start, initial board, verbose]
        """
        self.game = Hex(params[0])
        self.episodes = params[1]
        self.simulations = params[2]
        if params[3] == 3:
            self.initial_player = random.randint(1, 2)
        else:
            self.initial_player = params[3]
        self.player = copy.deepcopy(self.initial_player)
        self.mcts = MCTS_ANET(self, self.state_player(), params[4:8], self.game.layers, int(self.episodes/(params[8]-1))) # Endret siste param her, sånn at vi får 0,50,100,150 og 200.
        self.winner = []

    def run(self):
        """ Running the simulation G times.
        """
        for i in tqdm(range(self.episodes)):
            while not self.game.game_over(self.game.get_board()):
                if not self.game.initial_game():
                    self.mcts.set_new_root(self.state_player())
                action = self.mcts.simulate(self.simulations)
                self.game.do_move(action, self.player)
                state = self.state_player()
                dist = self.mcts.ANET.distribution(state)
                self.player = (self.player % 2) + 1

                print("Dist: ", dist, sum(dist[0]), dist.argmax())
                print("Board: ", state)
                print("Processed board: ", self.mcts.ANET.process_x(state))

            self.mcts.train(i)

            print("Final path: ", self.game.final_path)
            print("Final board: ", self.game.get_board())

            #self.game.draw((self.player % 2) + 1)
            self.winner.append(self.player % 2 + 1)
            if True:
                print("\nPlayer " + str(self.player % 2 + 1) + " wins \n")

            if i != self.episodes - 1:
                self.game.reset_game()
                self.player = copy.deepcopy(self.initial_player)
                self.mcts.reset(self.state_player())

        if self.game.game_over(self.game.get_board()):
            self.print_winner_statistics()

    def print_winner_statistics(self):
        print("\nPlayer 1 wins: ", self.winner.count(1))
        print("Player 2 wins: ", self.winner.count(2))
        percent = self.winner.count(1) / (self.winner.count(1) + self.winner.count(2)) * 100
        if self.winner.count(1) >= self.winner.count(2):
            print("Player 1 wins " + str(int(percent)) + " percent of the games \n")
        else:
            print("Player 2 wins " + str(100 - int(percent)) + " percent of the games \n")

    def state_player(self):
        state = self.game.get_board()
        state.insert(0, self.player)
        return state

    def get_child_action_pair(self, state):
        """ Finds all children of a state and the action leading to each child.

        :param state: state to find children from
        :return: list of tuples, (state, action)
        """
        state, player = process_state(state)

        if self.game.game_over(state):
            return []
        else:
            states = []
            actions = self.game.child_actions(state, player)
            for a in actions:
                new_state = copy.deepcopy(state)
                new_state = self.game.do_action(new_state, a[0], a[1])
                new_state.insert(0, (player % 2) + 1)
                states.append((new_state, a))
            return states

    def get_actions(self, state):
        """ Produces a list of possible actions from a state

        :param state: state to find actions from
        :return: list of actions
        """
        state, player = process_state(state)
        return self.game.child_actions(state, player)

    def get_random_action(self, state):
        """ Produces a random action of possible actions from a state

        :param state: state to find action from
        :return: 1 action
        """
        state, player = process_state(state)
        actions = self.game.child_actions(state, player)
        return actions[random.randint(0, len(actions)-1)]

    def is_win(self, state):
        """ Checks if a game is finished.

        :param state: last state to check if is final
        :return:
        """
        state, player = process_state(state)
        return self.game.game_over(state)

    def do_action(self, state, action):
        """ Perform an action in game

        :param state: state to perform action from
        :param action: action to perform
        :return: updated state after action is performed
        """
        state, player = process_state(state)
        state = self.game.do_action(state, action[0], player)
        state.insert(0, (player % 2) + 1)
        return state


def process_state(state):
    s = copy.deepcopy(state)
    player = s.pop(0)
    return s, player


def play(itt):
    game = Hex(3)
    player = 1
    model = ANET(0.9, (10,15,20), 'linear', 'sgd', 3)
    model.load_model(itt)
    board = copy.deepcopy(game.get_board())
    board.insert(0, 1)
    while not game.game_over(game.get_board()):
        game.draw(player)
        print(player)
        if player == 2:
            action = int(input("Velg move: "))
        else:
            dist = model.distribution(board)
            actions = game.child_actions(copy.deepcopy(game.get_board()), player)
            action = distibution_to_action(dist, actions)[0]
            print(action)
        game.do_move(action, player)
        board[action] = player
        player = (player % 2) + 1

    game.draw(player%2 + 1)


g = Game()
g.run()
#play(100)