from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from Assignment1.RL.SplitGD import SplitGD
import numpy as np
import tensorflow as tf



class Critic:

    def __init__(self, learning_rate, eligibility_rate, discount_factor, table_critic, layers_NN, size):
        """ Initialize Critic-object

        :param learning_rate: Input from parameters.txt
        :param eligibility_rate: Input from parameters.txt
        :param discount_factor: Input from parameters.txt
        :param table_critic: Input from parameters.txt
        :param layers_NN: Input from parameters.txt
        :param size: Input from parameters.txt
        """
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = tf.Variable(discount_factor, dtype=tf.float32)
        self.table_critic = table_critic
        self.layers = layers_NN
        self.size = size
        self.values = {}
        self.eligibilities = {}
        self.delta = 0
        self.zero = tf.Variable(0, dtype=tf.float32)
        if not self.table_critic:
            self.model = self.build_model()

    def calculate_delta(self, reward, next_state, state):
        """ Calculate TD-error according to δ ← r +γV(s')−V(s). Delta = reward if in goal state.

        :param reward: int, reward in state
        :param next_state: next state
        :param state: current state
        :return: int, TD-error
        """

        if next_state is None:
            self.delta = reward
        else:
            if self.table_critic:
                state_value = self.values[state]
                next_state_value = self.values[next_state]
            else:
                state_value = self.model.model(np.array([state])[0:1]).numpy()[0][0]
                next_state_value = self.model.model(np.array([next_state])[0:1]).numpy()[0][0]

            self.delta = reward + self.discount_factor.numpy() * next_state_value - state_value

    def change_value(self, state, path, reward):
        """ Calculate state-value based on formula: V(s) ← V(s)+ αcδe(s)

        :param state: current state
        :param path: path from state to end
        :param reward: reward in state
        """

        reward = tf.Variable(reward, dtype=tf.float32)

        # For table-based:
        if self.table_critic:
            self.values[state] = self.values[state] + self.learning_rate * self.delta * self.eligibilities[state]

        # For NN, fit for each state:
        else:
            for j in range(len(path)-1):
                itt_state, itt_action = path[j]
                if j == len(path) - 1:
                    target = reward
                else:
                    itt_next_state, itt_next_action = path[j + 1]
                    value = self.model.model(np.array([itt_next_state])[0:1])
                    target = tf.math.add(reward, tf.math.multiply(self.discount_factor, value))

                self.model.fit([np.array(itt_state)], [target], self.delta, self.learning_rate, verbose=False)

    def update_eligibility(self, state):
        """ Update eligibility value based on formula: e(s) ← γλe(s)

        :param state: current state
        """
        self.eligibilities[state] = self.discount_factor.numpy() * self.eligibility_rate * self.eligibilities[state]

    def build_model(self):
        """ Bulid the NN model using the SplitGD/keras model with given hidden nodes etc.

        :return: The NN model
        """
        model = Sequential()

        # Input layer to the model:
        model.add(Dense(self.layers[0], input_dim=self.size**2, activation='sigmoid'))

        for i in range(1, len(self.layers)):
            model.add(Dense(self.layers[i], activation='sigmoid'))

        model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])

        return SplitGD(model)

    def reset_eligibilities(self):
        """ Only resets eligibilities for table_based. NN better if not reset.
        """
        if self.table_critic:
            for key in self.eligibilities.keys():
                self.eligibilities[key] = 0
