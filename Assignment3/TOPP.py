import copy
import numpy as np
from Assignment3.hex import Hex
from Assignment3.ANET import ANET
from Assignment3.MCTS_ANET import distibution_to_action


class TOPP:

    def __init__(self, episodes, m, g, k):
        self.episodes = episodes
        self.saves = m
        self.games = g
        self.layers = k

        self.winners = {}
        self.statistics = [0 for j in range(self.saves)]
        for i in range(self.saves):
            self.winners[i*int(self.episodes/(self.saves-1))] = 0
            self.statistics[i] = [0 for j in range(self.saves)]

    def run_topp(self, verbose=False):
        for i, itt1 in enumerate(self.winners):
            for j, itt2 in enumerate(self.winners):
                if itt2 < itt1:
                    print(itt1,itt2)
                    for g in range(self.games):
                        if g % 2 == 0:
                            winner = self.play(itt1, itt2, verbose)
                            if winner == 1:
                                print("Itt:", itt1, "won over itt:", itt2, "- Itt", itt1, "started")
                                self.winners[itt1] += 1
                                self.statistics[i][j] += 1
                            else:
                                print("Itt:", itt2, "won over itt:", itt1, "- Itt", itt1, "started")
                                self.winners[itt2] += 1
                                self.statistics[j][i] += 1
                        else:
                            winner = self.play(itt2, itt1, verbose)
                            if winner == 1:
                                print("Itt:", itt2, "won over itt:", itt1, "- Itt", itt2, "started")
                                self.winners[itt2] += 1
                                self.statistics[j][i] += 1
                            else:
                                print("Itt:", itt1, "won over itt:", itt2, "- Itt", itt2, "started")
                                self.winners[itt1] += 1
                                self.statistics[i][j] += 1

        self.print_results()

    def play(self, itt1, itt2, verbose=False):
        game = Hex(self.layers)
        player = 1
        model1 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model1.load_model(itt1)
        model2 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model2.load_model(itt2)

        board = copy.deepcopy(game.get_board())
        board.insert(0, player)
        while not game.game_over(game.get_board()):
            if verbose:
                game.draw(player, itt1, itt2)
            if player == 1:
                dist = model1.distribution(board)
                actions = game.child_actions(copy.deepcopy(game.get_board()), player)
                action = distibution_to_action(dist, actions)[0]
            else:
                dist = model2.distribution(board)
                actions = game.child_actions(copy.deepcopy(game.get_board()), player)
                action = distibution_to_action(dist, actions)[0]
            game.do_move(action, player)
            board[action+1] = player
            player = (player % 2) + 1
            board[0] = player
        game.draw(game.winner, itt1, itt2)
        return game.winner

    def print_results(self):
        print("There was played a total of " + str(int((self.saves * (self.saves-1))/2)) + " series of "
              + str(self.games) + " games.")

        for key in self.winners:
            print("The ANET trained for " + str(key) + " episodes won " + str(self.winners[key]) + " games.")

        print("\n  W / L |" + ''.join(['I-{:<3}|'.format(item) for item in self.winners]) + " Tot |")
        keys = list(self.winners.keys())
        for i, row in enumerate(self.statistics):
            print('-'*8 + ''.join([ '|'+'-'*5 for item in self.winners]) + '-'*7)
            print("  I-{:<3} |".format(keys[i]) + ''.join([''.join(['{:^5}|'.format(item) for item in row])]) + '{:^5}|'.format(sum(row)))




t = TOPP(100, 5, 10, 4)
t.run_topp(False)
