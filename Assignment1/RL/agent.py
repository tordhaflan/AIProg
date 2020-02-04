import random

from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.player import Player
from Assignment1.SimWorld.board import Board


class Agent:

    def __init__(self, parameters):
        """
        :param parameters: [size, board_type, open_cells, episodes, layers, initial_epsilon,
                            actor_learning_rate, actor_eligibility_rate, actor_discount_factor,
                            critic_learning_rate, critic_eligibility_rate, critic_discount_factor]
        """

        self.sim_world = Player(Board(parameters[0:2]), parameters[2])  # for now, player object
        self.episodes = parameters[3]
        self.layers = parameters[4]
        self.initial_epsilon = parameters[5]
        self.actor = Actor(parameters[6:9])
        self.critic = Critic(parameters[9:])

        self.initial_state = self.sim_world.get_binary_board()  # tuple (converts playboard to a long tuple)

    def train(self):
        self.critic.values[self.initial_state] = random.randint(1, 10) / 100
        initial_actions = self.sim_world.get_moves()
        for action in initial_actions:
            self.actor.values[self.initial_state + action] = 0

        for i in range(self.episodes):
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)

            action = get_initial_action(initial_actions, self.initial_state, self.actor.value)
            while not self.sim_world.won():
                state = self.sim_world.do_move(action)
                actions = self.sim_world.get_moves()


def reset_eligibilities(actor, critic):
    for a in actor.keys():
        actor[a] = 0
    for c in critic.keys():
        critic[c] = 0

    return actor, critic


def get_initial_action(actions, state, actor_values):
    value = -1
    action = None
    for a in actions:
        if actor_values[state + a] > value:
            action = a

    return action
