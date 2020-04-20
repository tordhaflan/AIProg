from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import *
import tensorflow as tf
import numpy as np
import os

class ANET:

    def __init__(self, lr, layers, activation, optimizer, size):
        self.size = size
        self.input_dim = int(((size ** 2)*2)+2)
        self.name = str(size) + "_board"

        self.model = Sequential(name=self.name)

        # Input layer to the model:
        self.model.add(Dense(layers[0], input_dim=self.input_dim, activation=activation))

        #Hidden layers
        for i in range(1, len(layers)):
            self.model.add(Dense(layers[i], activation=activation))

        #Outputlayer
        self.model.add(Dense(self.size ** 2, activation='softmax'))

        self.model.compile(optimizer=make_optimizer(optimizer, lr), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

        self.class_weights = np.zeros(self.size**2)+(1/self.size**2)


    def distribution(self, x):
        """
        Method to produce a prediction
        """
        dist = self.model(self.process_x(x))
        return dist.numpy()

    def train(self, X, Y):
        """
        Training method with a minibatch (currently trainig on the whole training set, since it only consist of one instance of every state)
        """
        x_train, y_train = self.make_mini_batch(X, Y, 1.0)
        self.model.fit(x_train, y_train, epochs=10)

    def process_x(self, X):
        """
        Converting the state to a binary array
        """
        processed_x = np.zeros(self.input_dim)

        for i, x in enumerate(X):
            if x == 1:
                processed_x[i*2] = 1
            elif x == 2:
                processed_x[(i*2)+1] = 1

        return tf.convert_to_tensor(processed_x.reshape((1,self.input_dim)), dtype=tf.float32)

    def make_mini_batch(self, X, Y, percentage=0.8):
        """
        making a random mini batch of the traning set, default set to 0.8
        """
        indicies = np.arange(0, len(Y))
        np.random.shuffle(indicies)
        indicies = indicies[:int(np.floor(percentage*(len(Y))))]

        x_train = []
        y_train = []

        for i in indicies:
            x_train.append(self.process_x(X[i]))
            y_train.append(np.asarray(Y[i]).reshape((1,self.size**2)))

        return tf.convert_to_tensor(np.array(x_train).reshape((len(x_train), self.input_dim)), dtype=tf.float32), \
               tf.convert_to_tensor(np.array(y_train).reshape((len(y_train), self.size**2)), dtype=tf.float32)

    def save_model(self, episode):
        path = os.path.abspath('../Assignment3/Models/Hex_' + str(self.size)) + '/' + str(episode) + "_episodes.h5"
        name = self.name + "_" + str(episode) + "_episodes"
        self.model._name = name
        self.model.save(path)

    def load_model(self, episode):
        path = os.path.abspath('../Assignment3/Models/Hex_' + str(self.size)) + '/' + str(episode) + "_episodes.h5"
        self.model = load_model(path)


def make_optimizer(name, lr):
    if name == 'sgd':
        return SGD(learning_rate=lr, momentum=0.9)
    elif name == 'Adagrad':
        return Adagrad(learning_rate=lr)
    elif name == 'RMSProp':
        return RMSprop(learning_rate=lr)
    elif name == 'Adam':
        return Adam(learning_rate=lr)
