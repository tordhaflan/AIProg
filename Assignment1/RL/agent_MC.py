import copy
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense
from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.player import Player
from Assignment1.RL.read import read_parameters_file
from Assignment1.RL.SplitGD import SplitGD


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
        self.table_critic = parameters[4]
        self.actor = Actor(parameters[6], parameters[7], parameters[8])
        self.critic = Critic(parameters[9], parameters[10], parameters[11])
        self.parameters = parameters

        self.state_action = {}
        self.random_episodes = {}
        self.epsilon = copy.deepcopy(self.initial_epsilon)
        self.initial_state = self.sim_world.get_binary_board()  # tuple (converts playboard to a long tuple)
        if not self.table_critic:
            self.model = self.build_model()

    #  The learning process itself. Taken from pseudo-code in actor-critic.pdf
    def train(self):

        #  Initialize state
        self.critic.values[self.initial_state] = random.randint(1, 10) / 100
        initial_actions = self.sim_world.get_moves()
        if len(initial_actions) == 0:
            self.sim_world.show_game(None, None, self.parameters, False)
            return
        self.actor.set_values(self.initial_state, initial_actions)

        #  For each episode
        for i in range(self.episodes):
            path = []

            #TODO
            # Forklare modulo
            # Updates randomness factor over the course of episodes. Less randomness in later episodes, zero in last
            if self.initial_epsilon != 0:
                if i % int(self.initial_epsilon * self.episodes) == 0 and i != 0 or i == self.episodes - 1:
                    self.epsilon -= self.initial_epsilon ** 2
                    print(i+1, self.epsilon)

            #  Set e to 0. Set to 1 later if state is visited
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)
            # First move
            action, self.random_episodes = get_best_action(self.actor.values, self.initial_state, initial_actions, self.epsilon, self.random_episodes, i)
            path.append((self.initial_state, action))
            #TODO
            # Flyttes inn i whilen slik at vi følger pseudo og endrer state i første linje
            state = self.sim_world.do_move(action)

            # Runs until it reaches a final state.
            while not self.sim_world.game_over():
                actions = self.sim_world.get_moves()
                if not self.critic.values.keys().__contains__(state):
                    self.critic.values[state] = random.randint(1, 10) / 100
                    self.actor.set_values(state, actions)
                action, self.random_episodes = get_best_action(self.actor.values, state, actions, self.epsilon, self.random_episodes, i)
                self.actor.eligibilities[state + action] = 1
                self.critic.eligibilities[state] = 1
                path.append((state, action))
                state = self.sim_world.do_move(action)

            previous_state = None
            previous_action = None

            #TODO
            # Denne kan bare flyttes ut av for-loopen

            # If it is the final episode, saves the path for visualization
            if i == self.episodes - 1:
                final_path = []
                for pair in path:
                    final_path.append(pair[1])
            if self.table_critic:

                # Her kommer en if med NN vs. table
                # Updates SAP-values and State-values by back-propagating
                #TODO
                # Gå igjennom path listen baklengs, ikke poppe
                for j in range(len(path)):
                    #TODO
                    # Settes til state, action = path[j]
                    state, action = path.pop()

                    #TODO
                    # Skrive om slika at ifen sjekker end_state ikke j==0 for å gi reward
                    #Reward to final state
                    if j == 0:
                        reward = self.sim_world.get_reward(j)

                    # Discounted reward for other states
                    else:
                        #reward = self.sim_world.get_reward(j)
                        reward = 0
                        self.critic.update_eligibility(state, previous_state)
                        self.actor.update_eligibility(state, action, previous_state, previous_action)

                    # Update TD Error, State-values and SAP-values
                    self.critic.calculate_delta(reward, previous_state, state)
                    self.critic.change_value(state)
                    self.actor.change_value(state, action, self.critic.delta)

                    previous_state = state
                    previous_action = action
            else:
                state_list=[]
                target_list = []
                for j in range(len(path)):
                    state, action = path.pop()
                    state = np.array(list(state))

                    state_list.append(state)
                    target_list.append(j)

                state_list = np.array(state_list)
                target_list = np.array(target_list)


                self.model.fit(state_list, target_list, 10)

        print("Number of states visited:", len(self.actor.values.keys()))
        self.sim_world.show_game(final_path, self.parameters, True, self.random_episodes)
        print(self.epsilon)

    def build_model(self):
        model = Sequential()

        # Input layer to the model:
        model.add(Dense(self.layers_NN[0], input_dim=self.parameters[0]**2, activation='relu'))

        for i in range(1, len(self.layers_NN)):
            model.add(Dense(self.layers_NN[i], activation='relu',))

        model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])

        return SplitGD(model)



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
    for action in actions:
        if actor_values[state + action] >= value:
            best_action = action
            value = actor_values[state + action]
    randomness = random.randint(1, 100) > np.ceil(epsilon*100)
    if not randomness:
        random_moves[i] = 1
        return actions[random.randint(0, len(actions)-1)], random_moves
    else:
        return best_action, random_moves


main()
