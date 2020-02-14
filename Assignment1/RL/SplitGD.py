import math
import tensorflow as tf
import numpy as np


# ************** Split Gradient Descent (SplitGD) **********************************
# This "exposes" the gradients during gradient descent by breaking the call to "fit" into two calls: tape.gradient
# and optimizer.apply_gradients.  This enables intermediate modification of the gradients.  You can find many other
# examples of this concept online and in the (excellent) book "Hands-On Machine Learning with Scikit-Learn, Keras,
# and Tensorflow", 2nd edition, (Geron, 2019).

# This class serves as a wrapper around a keras model.  Then, instead of calling keras_model.fit, just call
# SplitGD.fit.  To use this class, just subclass it and write your own code for the "modify_gradients" method.

class SplitGD():

    def __init__(self, keras_model):
        self.model = keras_model
        """
        self.weights = [tf.convert_to_tensor(self.model.trainable_weights[i].numpy()) for i in range(0,len(self.model.trainable_weights),2)]
        self.eligebilities = [tf.convert_to_tensor(np.zeros(x.shape), dtype=tf.float32) for x in self.weights]
        
        """

        self.eligebilities = [tf.convert_to_tensor(np.zeros(self.model.trainable_weights[i].numpy().shape), dtype=tf.float32) for i in range(0,len(self.model.trainable_weights),2)]
    # Subclass this with something useful.
    def modify_gradients(self, gradients, learning_rate, td_error, discount_rate):
        """
         if len(self.weights) == 0:
            for i in range(0, len(gradients), 2):
                self.weights.append(gradients[i].numpy())
                self.eligebilities.append(np.ones(gradients[i].numpy().shape))
            self.weights = np.array(self.weights)
            self.eligebilities = np.array(self.eligebilities)

        for i in range(len(self.weights)):

            self.eligebilities[i] = np.add(self.eligebilities[i], gradients[i].numpy())
            error = np.dot(td_error, self.eligebilities[i])
            self.weights[i] = np.add(self.weights[i], error)
            self.eligebilities[i] = learning_rate * discount_rate * self.eligebilities[i]

            gradients[i] = self.weights[i]

        --------------------------------
        td_error = tf.Variable(td_error)
        change = tf.Variable(learning_rate * discount_rate, dtype=tf.float32)

        self.eligebilities = [tf.scalar_mul(td_error, tf.math.add(self.eligebilities[i], gradients[i*2])) for i in
                              range(len(self.eligebilities))]
        self.weights = [tf.math.add(self.weights[i], self.eligebilities[i]) for i in range(len(self.weights))]
        self.eligebilities = [tf.math.scalar_mul(change, self.eligebilities[i]) for i in range(len(self.eligebilities))]

        --------------------------------
        self.eligebilities = np.add(self.eligebilities, gradients)
        self.weights = np.add(self.weights, np.dot(td_error, self.eligebilities))
        self.eligebilities = np.dot(self.eligebilities, learning_rate * discount_rate)
        """
        td_error = tf.Variable(td_error, dtype=tf.float32)
        learning_rate = tf.Variable(learning_rate, dtype=tf.float32)
        gradient_weights = [tf.math.divide(gradients[i], -td_error) for i in range(0,len(gradients),2)]
        #delta_eligibilities = [tf.math.subtract(self.eligebilities[i], gradient_weights[i]) for i in range(len(gradient_weights))]

        self.eligebilities = [tf.math.add(self.eligebilities[i], gradient_weights[i]) for i in
                              range(len(self.eligebilities))]
        change = tf.multiply(td_error, learning_rate)
        for i in range(len(self.eligebilities)):
            #gradients[i*2] = tf.math.add(gradients[i*2], delta_eligibilities[i])
            #gradients[i*2] = tf.math.multiply(td_error, self.eligebilities[i])
            gradients[i*2] = tf.math.multiply(self.eligebilities[i], change)

        return gradients

    # This returns a tensor of losses, OR the value of the averaged tensor.  Note: use .numpy() to get the
    # value of a tensor. features = state, target = reward+discount factor*value(next state)
    def gen_loss(self, features, targets, avg=False):
        predictions = self.model(features[0:1])# Feed-forward pass to produce outputs/predictions
        loss = self.model.loss_functions[0](targets, predictions)
        return tf.reduce_mean(loss).numpy() if avg else loss

    def fit(self, features, targets, td_error, learning_rate, discount_rate, epochs=1, mbs=1, vfrac=0.1, verbose=True):
        params = self.model.trainable_weights
        train_ins, train_targs, val_ins, val_targs = split_training_data(features, targets, vfrac=vfrac)
        for _ in range(epochs):
            for _ in range(math.floor(epochs / mbs)):
                with tf.GradientTape() as tape:  # Read up on tf.GradientTape !
                    feaset, tarset = gen_random_minibatch(train_ins, train_targs, mbs=mbs)
                    loss = self.gen_loss(feaset, tarset, avg=False)
                    gradients = tape.gradient(loss, params)
                    gradients = self.modify_gradients(gradients, learning_rate, td_error, discount_rate)
                self.model.optimizer.apply_gradients(zip(gradients, params))
            if verbose: self.end_of_epoch_display(train_ins, train_targs, val_ins, val_targs)

    # Use the 'metric' to run a quick test on any set of features and targets.  A typical metric is some form of
    # 'accuracy', such as 'categorical_accuracy'.  Read up on Keras.metrics !!
    # Note that the model.metrics__names slot includes the name of the loss function (as 0th entry),
    # whereas the model.metrics slot does not include the loss function, hence the index+1 in the final line.
    # Use your debugger and go through the long list of slots for a keras model.  There are a lot of useful things
    # that you have access to.

    def gen_evaluation(self, features, targets, avg=False, index=0):
        predictions = self.model(features)
        evaluation = self.model.metrics[index](targets, predictions)
        #  Note that this returns both a tensor (or value) and the NAME of the metric
        return (tf.reduce_mean(evaluation).numpy() if avg else evaluation, self.model.metrics_names[index + 1])

    def status_display(self, features, targets, mode='Train'):
        print(mode + ' *** ', end='')
        print('Loss: ', self.gen_loss(features, targets, avg=True), end=' : ')
        val, name = self.gen_evaluation(features, targets)
        print('Eval({0}): {1} '.format(name, val))

    def end_of_epoch_display(self, train_ins, train_targs, val_ins, val_targs):
        self.status_display(train_ins, train_targs, mode='Train')
        if len(val_ins) > 0:
            self.status_display(val_ins, val_targs, mode='Validation')


# A few useful auxiliary functions

def gen_random_minibatch(inputs, targets, mbs=1):
    indices = np.random.randint(len(inputs), size=mbs)
    return inputs[indices], targets[indices]


# This returns: train_features, train_targets, validation_features, validation_targets
def split_training_data(inputs, targets, vfrac=0.1, mix=True):
    vc = round(vfrac * len(inputs))  # vfrac = validation_fraction
    # pairs = np.array(list(zip(inputs,targets)))
    if vfrac > 0:
        pairs = list(zip(inputs, targets))
        if mix: np.random.shuffle(pairs)
        vcases = pairs[0:vc];
        tcases = pairs[vc:]
        return np.array([tc[0] for tc in tcases]), np.array([tc[1] for tc in tcases]), \
               np.array([vc[0] for vc in vcases]), np.array([vc[1] for vc in vcases])
        #  return tcases[:,0], tcases[:,1], vcases[:,0], vcases[:,1]  # Can't get this to work properly
    else:
        return inputs, targets, [], []
