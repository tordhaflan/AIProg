import copy

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
        self.draw = {}
        for i in range(self.saves):
            self.winners[i*int(self.episodes/(self.saves-1))] = 0
            self.draw[i * int(self.episodes / (self.saves - 1))] = 0

    def run_topp(self):
        for itt1 in self.winners:
            for itt2 in self.winners:
                if itt2 < itt1:
                    print(itt1,itt2)
                    for g in range(self.games):
                        if g % 2 == 0:
                            winner = self.play(itt1, itt2)
                            if winner == 1:
                                print("Itt:", itt1, "won over itt:", itt2, "- Itt", itt1, "started")
                                self.winners[itt1] += 1
                            else:
                                print("Itt:", itt2, "won over itt:", itt1, "- Itt", itt1, "started")
                                self.winners[itt2] += 1
                        else:
                            winner = self.play(itt2, itt1)
                            if winner == 1:
                                print("Itt:", itt2, "won over itt:", itt1, "- Itt", itt2, "started")
                                self.winners[itt2] += 1
                            else:
                                print("Itt:", itt1, "won over itt:", itt2, "- Itt", itt2, "started")
                                self.winners[itt1] += 1

        self.print_results()

    def play(self, itt1, itt2):
        game = Hex(self.layers)
        player = 1
        model1 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model1.load_model(itt1)
        model2 = ANET(0.9, (10, 15, 20), 'linear', 'sgd', self.layers)
        model2.load_model(itt2)

        board = copy.deepcopy(game.get_board())
        board.insert(0, player)
        while not game.game_over(game.get_board()):
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
        game.draw(game.winner)
        return game.winner

    def print_results(self):
        print("There was played a total of " + str(int((self.saves * (self.saves-1))/2)) + " series of "
              + str(self.games) + " games.")

        for key in self.winners:
            print("The ANET trained for " + str(key) + " episodes won " + str(self.winners[key]) + " games.")


t = TOPP(200, 5, 10, 5)
t.run_topp()
