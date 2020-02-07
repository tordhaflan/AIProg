import copy
import numpy as np
import random
import matplotlib.pyplot as plt
from Assignment1.RL.actor import Actor
from Assignment1.RL.critic import Critic
from Assignment1.SimWorld.board import Board
from Assignment1.SimWorld.player import Player
from Assignment1.RL.read import read_parameters_file


class Agent:

    #  Initialisere Agent-objekt
    def __init__(self, parameters):
        """
        :param parameters: [size, board_type, open_cells, episodes, layers, initial_epsilon,
                            actor_learning_rate, actor_eligibility_rate, actor_discount_factor,
                            critic_learning_rate, critic_eligibility_rate, critic_discount_factor]
        """

        self.sim_world = Player(Board(parameters[0], parameters[1]), parameters[2])  # for now, player object
        self.episodes = parameters[3]
        self.layers = parameters[4]
        self.initial_epsilon = parameters[12]
        self.type_of_RL = parameters[5]
        self.actor = Actor(parameters[6], parameters[7], parameters[8])
        self.critic = Critic(parameters[9], parameters[10], parameters[11])
        self.parameters = parameters

        self.state_action = {}
        self.pegs_left = []
        self.epsilon = copy.deepcopy(self.initial_epsilon)
        self.initial_state = self.sim_world.get_binary_board()  # tuple (converts playboard to a long tuple)

    #  Selve læringsprosessen, psaudo-koden
    def train(self):
        #  init initial state
        self.critic.values[self.initial_state] = random.randint(1, 10) / 100
        initial_actions = self.sim_world.get_moves()
        self.actor.set_values(self.initial_state, initial_actions)

        #  For hver episode
        for i in range(self.episodes):
            path = []
            #  Setter el til 0, settes senere til 1 dersom den besøkes
            self.actor.eligibilities, self.critic.eligibilities = reset_eligibilities(self.actor.eligibilities,
                                                                                      self.critic.eligibilities)
            # Første move
            action = get_best_action(self.actor.values, self.initial_state, initial_actions, self.epsilon)
            path.append((self.initial_state, action))
            state = self.sim_world.do_move(action)

            # Kjører til end-state
            while not self.sim_world.game_over():
                actions = self.sim_world.get_moves()
                if not self.critic.values.keys().__contains__(state):
                    self.critic.values[state] = random.randint(1, 10) / 100
                    self.actor.set_values(state, actions)
                action = get_best_action(self.actor.values, state, actions, self.epsilon)
                self.actor.eligibilities[state + action] = 1
                self.critic.eligibilities[state] = 1
                path.append((state, action))
                state = self.sim_world.do_move(action)

            previous_state = None
            previous_action = None

            # Dersom siste episode, lagrer path
            if i == self.episodes - 1:
                final_path = []
                for pair in path:
                    final_path.append(pair[1])

            # oppdaterer SAP-values og state-values, back prop, dersom critic bruker table
            # Her kommer en if med NN vs. table
            for j in range(len(path)):
                state, action = path.pop()

                # Gi reward til siste state
                if j == 0:
                    reward, pegs_left = self.sim_world.get_reward()
                    self.pegs_left.append(pegs_left)

                # For andre enn den siste, gi discounted reward
                else:
                    reward = 0
                    self.critic.update_eligibility(state, previous_state)
                    self.actor.update_eligibility(state, action, previous_state, previous_action)

                # Oppdatere delta, SAP og state-value
                self.critic.calculate_delta(reward, previous_state, state)
                self.critic.change_value(state)
                self.actor.change_value(state, action, self.critic.delta)

                previous_state = state
                previous_action = action

            #TODO
            # Forklare modulo
            #Endrer epsilon for å få mindre random
            if i % int(self.initial_epsilon*self.episodes) == 0:
                print(i, self.epsilon)
                self.epsilon -= self.initial_epsilon ** 2

        print("Number of states visited:", len(self.actor.values.keys()))
        self.sim_world.show_game(final_path, self.pegs_left, self.parameters)
        print(self.epsilon)


# Kjøra spill
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


# Hjelpesak for å sette e til 0
def reset_eligibilities(actor, critic):
    for a in actor.keys():
        actor[a] = 0
    for c in critic.keys():
        critic[c] = 0

    return actor, critic


# Hjelpe for å finne best action, init med første value for å unngå None-state for best_action
# Returnerer best action eller random action basert på epsilon-verdi
def get_best_action(actor_values, state, actions, epsilon):
    value = actor_values[state + actions[0]]
    best_action = actions[0]
    for action in actions:
        if actor_values[state + action] >= value:
            best_action = action
            value = actor_values[state + action]
    return best_action if random.randint(0,100) > epsilon*100 else actions[random.randint(0,len(actions)-1)]


main()
