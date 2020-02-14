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

    #  Initialize Agent-object with parameters
    def __init__(self, parameters):
        """
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


    #  The learning process itself. Taken from pseudo-code in actor-critic.pdf
    def train(self):
        start_time = time.time()
        k = 0.05

        #  Initialize state
        initial_actions = self.sim_world.get_moves()
        if len(initial_actions) == 0:
            self.sim_world.show_game(None, None, self.parameters, False)
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
                    sys.stdout.write("\r Trainig done. \n")

                    self.epsilon = 0


            #  Set e to 0. Set to 1 later if state is visited
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)
            # First move
            action, self.random_episodes = get_best_action(self.actor.values, state, initial_actions,
                                                           self.epsilon, self.random_episodes, i)

            path.append((state, action))



            #TODO
            # Flyttes inn i whilen slik at vi følger pseudo og endrer state i første linje

            # Runs until it reaches a final state.
            while not self.sim_world.game_over():

                next_state, actions, reward = self.sim_world.do_move(action)

                if not self.critic.values.keys().__contains__(next_state):
                    if self.critic.table_critic:
                        self.critic.values[next_state] = random.randint(1, 10) / 100
                    self.actor.set_values(next_state, actions)

                if not self.sim_world.game_over():
                    next_action, self.random_episodes = get_best_action(self.actor.values, next_state, actions,
                                                                        self.epsilon, self.random_episodes, i)
                path.append((next_state, next_action))

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
                else:
                    self.actor.eligibilities[state + action] = 1
                    self.critic.calculate_delta(reward, next_state, state)
                    self.critic.change_value(state, path, reward)

                    for j in range(len(path)-2, -1, -1):
                        itt_state, itt_action = path[j]
                        self.actor.change_value(itt_state, itt_action, self.critic.delta)
                        self.actor.update_eligibility(itt_state, itt_action)

                    self.critic.reset_eligibilities()

                state = next_state
                action = next_action

            self.sim_world.game = copy.deepcopy(self.sim_world.initial_game)

            #print(self.actor.values.values())

        final_path = []
        for s, a in path:
            final_path.append(a)
        print(time.time()-start_time)
        print("Number of states visited:", len(self.actor.values.keys()))
        self.sim_world.show_game(final_path, self.parameters, True, self.random_episodes)
        print(self.epsilon)



# Runs and trains the agent
def main():
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


# Set e to 0.
def reset_eligibilities(actor, critic):
    for a in actor.keys():
        actor[a] = 0
    for c in critic.keys():
        critic[c] = 0

    return actor, critic


# Finds the best next action for a given state. Initialize with first possible action to avoid None-move.
def get_best_action(actor_values, state, actions, epsilon, random_moves, i):
    """
    :param actor_values: SAP-values
    :param state: Current state
    :param actions: Possible actions
    :param epsilon:
    :return: Best action or random action
    """
    value = actor_values[state + actions[0]]
    best_action = actions[0]
    #print(list(actor_values.keys()).index(state+best_action), "f", actor_values[state+best_action])
    for action in actions:
        if actor_values[state + action] > value:
            best_action = action
            value = actor_values[state + action]
    randomness = random.randint(1, 100) > np.ceil(epsilon*100)
    if not randomness:
        random_moves[i] = 1
        return actions[random.randint(0, len(actions)-1)], random_moves
    else:
        #print(list(actor_values.keys()).index(state+best_action), 'a', actor_values[state+best_action] )
        return best_action, random_moves




main()