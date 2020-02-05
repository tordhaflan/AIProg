import numpy as np
import random
import matplotlib.pyplot as plt
from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.board import Board
from Assignment1.SimWorld.player import Player


class Agent:

    def __init__(self, parameters):
        """
        :param parameters: [size, board_type, open_cells, episodes, layers, initial_epsilon,
                            actor_learning_rate, actor_eligibility_rate, actor_discount_factor,
                            critic_learning_rate, critic_eligibility_rate, critic_discount_factor]
        """

        self.sim_world = Player(Board(parameters[0], parameters[1]), parameters[2])  # for now, player object
        self.episodes = parameters[3]
        self.layers = parameters[4]
        self.initial_epsilon = parameters[5]
        self.actor = Actor(parameters[6], parameters[7], parameters[8])
        self.critic = Critic(parameters[9], parameters[10], parameters[11])

        self.state_action = {}
        self.pegs_left = []
        self.initial_state = self.sim_world.get_binary_board()  # tuple (converts playboard to a long tuple)

    def train(self):
        self.critic.values[self.initial_state] = random.randint(1, 10) / 100
        initial_actions = self.sim_world.get_moves()
        self.actor.set_values(self.initial_state, initial_actions)

        for i in range(self.episodes):
            path = []
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)

            action = get_best_action(self.actor.values, self.initial_state, initial_actions, self.initial_epsilon)
            path.append((self.initial_state, action))
            state = self.sim_world.do_move(action)
            while not self.sim_world.game_over():
                actions = self.sim_world.get_moves()
                if not self.critic.values.keys().__contains__(state):
                    self.critic.values[state] = random.randint(1, 10) / 100
                    self.actor.set_values(state, actions)
                action = get_best_action(self.actor.values, state, actions, self.initial_epsilon)
                self.actor.eligibilities[state + action] = 1
                self.critic.eligibilities[state] = 1
                path.append((state, action))
                state = self.sim_world.do_move(action)

            previous_state = None
            previous_action = None

            if i == self.episodes - 1:
                final_path = []
                for pair in path:
                    final_path.append(pair[1])

            for j in range(len(path)):
                state, action = path.pop()
                if j == 0:
                    reward, pegs_left = self.sim_world.get_reward()
                    self.pegs_left.append(pegs_left)
                else:
                    reward = 0
                    self.critic.update_eligibility(state, previous_state)
                    self.actor.update_eligibility(state, action, previous_state, previous_action)

                self.critic.calculate_delta(reward, previous_state, state)
                self.critic.change_value(state)
                self.actor.change_value(state, action, self.critic.delta)

                previous_state = state
                previous_action = action
        plot_peg_convergency(self.pegs_left)
        self.sim_world.show_game(final_path)

def reset_eligibilities(actor, critic):
    for a in actor.keys():
        actor[a] = 0
    for c in critic.keys():
        critic[c] = 0

    return actor, critic


def get_best_action(actor_values, state, actions, epsilon):
    value = actor_values[state + actions[0]]
    best_action = actions[0]
    for action in actions:
        if actor_values[state + action] >= value:
            best_action = action
            value = actor_values[state + action]
    return best_action if random.randint(0,100) > epsilon*100 else actions[random.randint(0,len(actions)-1)]

def plot_peg_convergency(pegs_left):
    x = np.arange(len(pegs_left))

    plt.plot(x, pegs_left)


A = Agent([5, True, [(2, 0)], 1000, None, 0.1, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9])

A.train()
