import copy
import numpy as np
import random
import sys
import time
from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.player import Player
from Assignment1.RL.read import read_parameters_file


class Agent:

    def __init__(self, parameters):
        """ Initialize Agent-object with parameters

        :param parameters: [size, board_type, open_cells, episodes, layers_NN, initial_epsilon,
                            actor_learning_rate, actor_eligibility_rate, actor_discount_factor,
                            critic_learning_rate, critic_eligibility_rate, critic_discount_factor]
        """
        self.sim_world = Player(parameters[0], parameters[1], parameters[2])
        self.episodes = parameters[3]
        self.layers_NN = parameters[5]
        self.initial_epsilon = parameters[12]
        self.actor = Actor(parameters[6], parameters[7], parameters[8])
        self.critic = Critic(parameters[9], parameters[10], parameters[11],
                             table_critic=parameters[4], layers_NN=parameters[5], size=parameters[0])
        self.parameters = parameters

        self.state_action = {}
        self.random_episodes = {}
        self.epsilon = copy.deepcopy(self.initial_epsilon)
        self.initial_state = self.sim_world.get_binary_board()  # tuple (converts playboard to a long tuple)

    def train(self, display=True):
        """ The learning process itself. Taken from pseudo-code in actor-critic.pdf.
            Updates actor and critic-values

        :param display: True if last episode
        :return: int pegs_left[-1], number of pegs in last episode
        """
        start_time = time.time()
        sys.stdout.write("Training started")
        sys.stdout.flush()

        k = 0.05

        #  Initialize state
        initial_actions = self.sim_world.get_moves()
        if len(initial_actions) == 0:
            self.sim_world.show_game(None, self.parameters, False, self.random_episodes)
            return

        if self.critic.table_critic:
            self.critic.values[self.initial_state] = random.randint(1, 10) / 100

        self.actor.set_values(self.initial_state, initial_actions)

        #  For each episode
        for i in range(self.episodes):
            path = []
            state = self.initial_state

            if self.initial_epsilon != 0:
                if i >= k * self.episodes:
                    self.epsilon = self.initial_epsilon * (1-k)
                    sys.stdout.write("\rProgress in training: " + str(round(k*100)) + "% | " +
                                     "Time spent: " + str(round(time.time()-start_time)) + "s")
                    sys.stdout.flush()
                    k += 0.05
                if i == self.episodes-1:
                    m, s = divmod(time.time()-start_time, 60)
                    sys.stdout.write("\r Trainig done. Total time: {}m {}s \n".format(int(m), int(s)))
                    self.epsilon = 0

            # Set e to 0. Set to 1 later if state is visited. Only reset critic e to 0 if table_critic.
            self.actor.reset_eligibilities()
            self.critic.reset_eligibilities()

            # First move
            action, self.random_episodes = get_best_action(self.actor.values, state, initial_actions,
                                                           self.epsilon, self.random_episodes, i)

            path.append((state, action))

            # Runs until it reaches a final state.
            while not self.sim_world.game_over():

                next_state, actions, reward = self.sim_world.do_move(action)

                if new_state(self.actor.values, next_state, actions):
                    self.critic.values[next_state] = random.randint(1, 10) / 100
                    self.actor.set_values(next_state, actions)

                if not self.sim_world.game_over():
                    next_action, self.random_episodes = get_best_action(self.actor.values, next_state, actions,
                                                                        self.epsilon, self.random_episodes, i)

                else:
                    next_action = None

                path.append((next_state, next_action))

                # For table-based critic:
                if self.critic.table_critic:
                    self.actor.eligibilities[state + action] = 1
                    self.critic.calculate_delta(reward, next_state, state)
                    self.critic.eligibilities[state] = 1

                    for j in range(len(path)-2, -1, -1):
                        itt_state, itt_action = path[j]
                        self.critic.change_value(itt_state, path, reward)
                        self.critic.update_eligibility(itt_state)
                        self.actor.change_value(itt_state, itt_action, self.critic.delta)
                        self.actor.update_eligibility(itt_state, itt_action)

                # For NN, do not update critic eligibility, but train NN.
                else:
                    self.actor.eligibilities[state + action] = 1
                    self.critic.calculate_delta(reward, next_state, state)
                    self.critic.change_value(state, path, reward)

                    for j in range(len(path)-2, -1, -1):
                        itt_state, itt_action = path[j]
                        self.actor.change_value(itt_state, itt_action, self.critic.delta)
                        self.actor.update_eligibility(itt_state, itt_action)

                state = next_state
                action = next_action

            # To reset the board for training.
            self.sim_world.game = copy.deepcopy(self.sim_world.initial_game)

        final_path = [a for s, a in path]
        print("Number of states visited:", len(self.actor.values.keys()))
        if display:
            self.sim_world.show_game(final_path, self.parameters, True, self.random_episodes)
        return self.sim_world.pegs_left[-1]


def main():
    """ Runs and trains the agent based on parameters.txt
    """

    parameters = read_parameters_file()
    layers = parameters[0]-1
    diamond = parameters[1]
    open_cells = []
    if type(parameters[2]) is not list:
        for i in range(parameters[2]):
            r = random.randint(0, layers)
            if diamond:
                c = random.randint(0, layers)
            else:
                c = random.randint(0, r)
            open_cells.append((r, c))
        parameters[2] = open_cells

    agent = Agent(parameters)
    agent.train()


def get_best_action(actor_values, state, actions, epsilon, random_moves, i):
    """ Finds the best next action for a given state. Initialize with first possible action to avoid None-move.
    :param actor_values: SAP-values
    :param state: Current state
    :param actions: Possible actions
    :param epsilon: randomness value
    :param random_moves: list with episode number where random move has been done.
    :param i: episode
    :return: Best action or random action
    """
    value = actor_values[state + actions[0]]
    best_action = actions[0]
    for action in actions:
        if actor_values[state + action] > value:
            best_action = action
            value = actor_values[state + best_action]

    randomness = random.randint(1, 100) > np.ceil(epsilon*100)
    if not randomness:
        random_moves[i] = 1
        return actions[random.randint(0, len(actions)-1)], random_moves
    else:
        return best_action, random_moves


def new_state(values, state, actions):
    """ Return true if state has not been visited before

    :param values: Actor-values
    :param state: Next state
    :param actions: possible actions
    :return: True if state has not been visited before
    """
    for action in actions:
        if values.keys().__contains__(state+action):
            return False
    return True


main()
