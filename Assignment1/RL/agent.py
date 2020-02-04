import random, copy

from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.player import Player
from Assignment1.SimWorld.board import Board, draw_board_final, draw_board


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
        self.set_actor_values(self.initial_state, initial_actions)

        for i in range(self.episodes):
            path = []
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)

            action = get_best_action(self.actor.values, self.initial_state, initial_actions)
            path.append((self.initial_state, action))
            state = self.sim_world.do_move(action)
            while not self.sim_world.game_over():
                actions = self.sim_world.get_moves()
                if not self.critic.values.keys().__contains__(state):
                    self.critic.values[state] = random.randint(1, 10) / 100
                    self.set_actor_values(state, actions)
                action = get_best_action(self.actor.values, state, actions)
                self.actor.eligibilities[state + action] = 1
                self.critic.eligibilities[state] = 1
                path.append((state, action))
                state = self.sim_world.do_move(action)

            previous_state = None
            previous_action = None

            if (i == self.episodes - 1):
                final_path = copy.deepcopy(path)

            for j in range(len(path)):
                state, action = path.pop()
                if j == 0:
                    reward = self.sim_world.get_reward()

                else:
                    reward = 0
                    self.critic.update_eligibility(state, previous_state)
                    self.actor.update_eligibility(state, action, previous_state, previous_action)

                self.critic.calculate_delta(reward, previous_state, state)
                self.critic.change_value(state)
                self.actor.change_value(state, action, self.critic.delta)

                previous_state = state
                previous_action = action

            if i % 100 == 0: print(i)

        for state, action in final_path:
            draw_board(self.sim_world.game, action[0], action[1])
            self.sim_world.make_move(action)
        draw_board_final(self.sim_world.game)

    def set_actor_values(self, state, actions):
        for action in actions:
            self.actor.values[state + action] = 0


def reset_eligibilities(actor, critic):
    for a in actor.keys():
        actor[a] = 0
    for c in critic.keys():
        critic[c] = 0

    return actor, critic


def get_best_action(actor_values, state, actions):
    value = -1
    best_action = None
    for action in actions:
        if actor_values[state + action] >= value:
            best_action = action
            value = actor_values[state + action]
    return best_action


A = Agent([4, True, [(2, 0)], 5000, None, 0.1, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9])

A.train()
