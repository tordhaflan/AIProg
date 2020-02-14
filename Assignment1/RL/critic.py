from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from Assignment1.RL.SplitGD import SplitGD
import numpy as np
import tensorflow as tf


class Critic:

    #  Initialize Critic-object
    def __init__(self, learning_rate, eligibility_rate, discount_factor, table_critic, layers_NN, size):
        """
        :param learning_rate: Input from parameters.txt
        :param eligibility_rate: Input from parameters.txt
        :param discount_factor: Input from parameters.txt
        """
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor
        self.table_critic = table_critic
        self.layers = layers_NN
        self.size = size
        self.values = {}
        self.eligibilities = {}
        self.delta = 0
        if not self.table_critic:
            self.model = self.build_model()

    #  Calculate TD-error. Delta = reward if in goal state.
    def calculate_delta(self, reward, next_state, state):

        if next_state is None:
            self.delta = reward
        else:
            if self.table_critic:
                state_value = self.values[state]
                next_state_value = self.values[next_state]
            else:
                state_value = self.model.model.predict(np.array([state]))[0][0]
                next_state_value = self.model.model.predict(np.array([next_state]))[0][0]

            self.delta = reward + self.discount_factor * next_state_value - state_value

    def change_value(self, state, path, reward):
        #  Update state-value based on formula: V(s) ← V(s)+ αcδe(s)
        if self.table_critic:
            self.values[state] = self.values[state] + self.learning_rate * self.delta * self.eligibilities[state]
        else:
            state_list = []
            target_list = []
            for j in range(len(path) - 1):
                itt_next_state, itt_next_action = path[j + 1]
                itt_state, itt_action = path[j]
                #if not self.values.keys().__contains__(itt_next_state):
                #    value = random.randint(1, 10) / 100
                #    self.values[itt_next_state] = 0
                #else:
                value = self.model.model.predict(np.array([itt_next_state]))[0][0]
                target = reward + self.discount_factor * value
                target_list.append(target)
                itt_state = np.array(itt_state)
                state_list.append(itt_state)

            state_list = np.array(state_list)
            target_list = np.array(target_list)

            print(target_list)

            self.model.fit(state_list, target_list, self.delta, self.learning_rate,
                           self.discount_factor, verbose=False)

    #  Update eligibility value based on formula: e(s) ← γλe(s)
    def update_eligibility(self, state):
        self.eligibilities[state] = self.discount_factor * self.eligibility_rate * self.eligibilities[state]

    def get_value(self, state):
        if self.table_critic:
            return self.values[state]
        else:
            return self.model.model.predict(np.array([state]))

    def build_model(self):
        model = Sequential()

        # Input layer to the model:
        model.add(Dense(self.layers[0], input_dim=self.size**2, activation='sigmoid'))

        for i in range(1, len(self.layers)):
            model.add(Dense(self.layers[i], activation='sigmoid'))
        sgd = SGD(learning_rate=0.9)
        model.compile(optimizer=sgd, loss='mean_squared_error', metrics=['accuracy'])

        return SplitGD(model)

    def reset_eligibilities(self):
        self.model.eligebilities = [
            tf.convert_to_tensor(np.zeros(self.model.model.trainable_weights[i].numpy().shape), dtype=tf.float32) for i in
            range(0, len(self.model.model.trainable_weights), 2)]