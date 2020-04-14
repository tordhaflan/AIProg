from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import *
import numpy as np
import os


#TODO
# Two entery nodes for the neural net (0/1,0/1, state)

class ANET:

    #TODO
    # Set right output dim (match prob distribution)
    def __init__(self, lr, layers, activation, optimizer, size):
        self.size = size
        #self.input_dim = ((size ** 2)*2)+2
        self.input_dim = (size ** 2)+1
        self.name = str(size) + "_board"
        self.model = Sequential(name=self.name)

        # Input layer to the model:
        self.model.add(Dense(layers[0], input_dim=self.input_dim, activation=activation))

        for i in range(1, len(layers)):
            self.model.add(Dense(layers[i], activation=activation))

        self.model.add(Dense(self.size ** 2, activation='softmax')) #adding last layer

        self.model.compile(optimizer=make_optimizer(optimizer, lr), loss='categorical_crossentropy')

        #self.model.summary()

    def distribution(self, x):
        #dist = self.model(self.process_x(x))
        dist = self.model(np.asarray(x).reshape((1,(self.size ** 2)+1)))
        return dist.numpy()

    def train(self, X, Y):
        x_train, y_train = self.make_mini_batch(X, Y)
        self.model.fit(x_train, y_train, epochs=100)
        #for i in range(len(y_train)):
        #    print("Training data: ", x_train[i], y_train[i])
        #    self.model.fit(x_train[i], y_train[i])

    def process_x(self, X):
        processed_x = np.zeros(self.input_dim)

        for i, x in enumerate(X):
            if x == 1:
                processed_x[i*2] = 1
            elif x == 2:
                processed_x[(i*2)+1] = 1

        return processed_x.reshape((1,self.input_dim))

    def make_mini_batch(self, X, Y, percentage=0.8):
        indicies = np.arange(0, len(Y)-1)
        np.random.shuffle(indicies)
        indicies = indicies[:int(np.floor(percentage*(len(Y))))]

        x_train = []
        y_train = []

        for i in range(len(Y)):
            if indicies.__contains__(i):
                #x_train.append(self.process_x(X[i]))
                x_train.append(np.asarray(X[i]).reshape((1,(self.size ** 2)+1)))
                y_train.append(np.asarray(Y[i]).reshape((1,self.size**2)))

        return np.concatenate(x_train), np.concatenate(y_train)

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
        return SGD(learning_rate=lr)
    elif name == 'Adagrad':
        return Adagrad(learning_rate=lr)
    elif name == 'RMSProp':
        return RMSprop(learning_rate=lr)
    elif name == 'Adam':
        return Adam(learning_rate=lr)
