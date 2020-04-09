import copy
import random

from Assignment3.hex import Hex
from Assignment3.ANET import ANET
from Assignment3.MCTS_ANET import MCTS_ANET, distibution_to_action


class TOPP:

    def __init__(self, episodes, m, g, k):
        self.episodes = episodes
        self.saves = m
        self.games = g
        self.layers = k

        self.winners = {}
        for i in range(self.saves):
            self.winners[i*int(self.episodes/(self.saves-1))] = 0



    def run_TOPP(self):
        pass

    def play(self, itt1, itt2):
        game = Hex(self.layers)
        player = 1

        # TODO
        # Finne ut hva som skal være input, må vel være samme som de er trent på?
        model1 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model1.load_model(itt1)
        model2 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model2.load_model(itt2)

        board = copy.deepcopy(game.get_board())
        board.insert(0, 1)
        while not game.game_over(game.get_board()):
            game.draw(player)
            print(player)
            if player == 1:
                dist = model1.distribution(board)
                actions = game.child_actions(copy.deepcopy(game.get_board()), player)
                action = distibution_to_action(dist, actions)[0]
            else:
                dist = model2.distribution(board)
                actions = game.child_actions(copy.deepcopy(game.get_board()), player)
                action = distibution_to_action(dist, actions)[0]
                print(action)
            game.do_move(action, player)
            board[action] = player
            player = (player % 2) + 1

        return (player % 2) + 1

