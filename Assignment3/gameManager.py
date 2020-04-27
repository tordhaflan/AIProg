import copy
import random
import os
import csv
import numpy as np
from tqdm import tqdm
from tensorflow.keras.models import load_model
from Assignment3.hex import Hex, draw_board
from Assignment3.read_file import read_file
from Assignment3.MCTS_ANET import MCTS_ANET, distibution_to_action
from Assignment3.ANET import ANET


class Game:

    def __init__(self, params=read_file()):
        """
        Initialize game manager from txt file
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
        self.delta = 0.25

    def run(self):
        """
        Running the simulation G times.
        """
        for i in tqdm(range(self.episodes)):
            time_sim = copy.deepcopy(self.simulations)
            while not self.game.game_over(self.game.get_board()):
                if not self.game.initial_game():
                    self.mcts.set_new_root(self.state_player())
                action = self.mcts.simulate(time_sim)
                self.game.do_move(action, self.player)
                self.player = (self.player % 2) + 1
                time_sim -= self.delta

            self.mcts.train(i)

            print("Final path: ", self.game.final_path)
            print("Final board: ", self.game.get_board())

            #Sett denne opp for å visualisere hvert game
            #self.game.draw((self.player % 2) + 1)
            self.winner.append(self.player % 2 + 1)
            print(self.winner)
            if True:
                print("\nPlayer " + str(self.winner[-1]) + " wins \n")

            if i != self.episodes - 1:
                self.game.reset_game()
                self.initial_player = (self.initial_player % 2) + 1
                self.player = copy.deepcopy(self.initial_player)
                self.mcts.reset(self.state_player())

            #if i > self.episodes/2:
            #    self.simulations = 60
            #    self.delta = 3
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
    """
    Removes player from the state
    """
    s = copy.deepcopy(state)
    player = s.pop(0)
    return s, player


def play(itt, board_size, start=1, model=None):
    """
    Method so that one can play agianst a version of the NN
    """
    game = Hex(board_size)
    player = 1
    if model is None:
        model = ANET(0.9, (10,15,20), 'linear', 'sgd', board_size)
        model.load_model(itt)
    board = copy.deepcopy(game.get_board())
    board.insert(0, player)
    while not game.game_over(game.get_board()):
        game.draw(player)
        if player == start:
            inn = ""
            while not inn.isdigit():
                inn = input("Velg move: ")
            action = int(inn)
        else:
            dist = model.distribution(board)
            with np.printoptions(precision=3, suppress=True):
                print("Dist: ", dist, dist.argmax())
            actions = game.child_actions(copy.deepcopy(game.get_board()), player)
            action = distibution_to_action(dist, actions)[0]
        game.do_move(action, player)
        if board[action+1] == 0:
            board[action+1] = player
            player = (player % 2) + 1
            board[0] = player
        print("Board: ", board, len(board))
    game.draw(player%2 + 1)


def save_RBUF(RBUF, size):
    path = os.path.abspath('../Assignment3/RBUF/RBUF_' + str(size) + ".csv")
    file_obj = open(path, 'a', newline='')

    writer = csv.writer(file_obj, quoting=csv.QUOTE_ALL)

    for state, dist in RBUF:
        writer.writerow(state)
        writer.writerow(dist)
    file_obj.close()


def load_RBUF(size):
    path = os.path.abspath('../Assignment3/RBUF/RBUF_' + str(size) + ".csv")
    RBUF = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = []
        for row in reader:
            rows.append(row)

    for i in range(0,len(rows), 2):
        state = [int(s) for s in rows[i]]
        dist = [float(d) for d in rows[i+1]]
        RBUF.append((state, dist))

    return RBUF
# -------- Main --------
#main for å kjøre spillet/simulering
g = Game()
g.run()
RBUF = g.mcts.RBUF

save_RBUF(RBUF, g.game.layers)

#Kommenter ut main og kjør denne, så kan du spille mot et NN (episoder, brettstørrelse)
#play(200, 5)
"""
lr = 0.0001
nn = ANET(lr, (1024, 1024, 1024, 1024, 1024), 'relu', 'Adam', 5)

RBUF = load_RBUF(5)

size = len(RBUF)

x_train = []
y_train = []

for i in range(size):
    x_train.append(RBUF[i][0])
    y_train.append(RBUF[i][1])

for i in range(4):
    nn.train(x_train, y_train, 50)

path = os.path.abspath('../Assignment3/RBUF/' + 'RBUF_5_' + str(lr) + '.h5')
name = "RBUF_5_" + str(lr)
nn.model._name = name
nn.model.save(path)
"""
"""
lr = 0.001
nn = ANET(lr, (1024, 1024, 1024, 1024, 1024), 'relu', 'Adam', 5)
path = os.path.abspath('../Assignment3/RBUF/' + 'RBUF_5_' + str(lr) + '.h5')
nn.model = load_model(path)
play(0,5, 2, nn)
"""




