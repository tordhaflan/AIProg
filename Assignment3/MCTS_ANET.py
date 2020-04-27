import random
import copy
import numpy as np
import time
import os
import csv
from Assignment3.ANET import ANET


class MCTS_ANET:

    def __init__(self, game, state, anet_config, size, save_interval):
        """Init MCTS-object

        :param game:
        :param state:
        """
        self.game_manager = game
        self.root_node = Node(state, None)
        self.ANET = ANET(anet_config[0], anet_config[1], anet_config[2], anet_config[3], size)
        self.RBUF = []
        self.save_interval = save_interval
        self.time = np.zeros(5)
        self.size = size

    def simulate(self, t):
        """ Simulation of M different tree-searches to determine a move

        :param m: amount of simulations
        """
        #self.time = np.zeros(5)
        start = time.time()
        self.expansion(self.root_node)
        while time.time() - start < t:
            leaf, moves = self.tree_search()
            if leaf.is_final_state:
                reward = self.evaluation(leaf, moves)
                self.backpropagation(leaf, reward)
            elif len(leaf.children) == 0:
                self.expansion(leaf)
                child = leaf.children[random.randint(0, len(leaf.children) - 1)]
                moves += 1
                reward = self.evaluation(child, moves)
                child.visits += 1
                self.backpropagation(child, reward)
            else:
                for child in leaf.children:
                    if child.visits == 0:
                        moves += 1
                        reward = self.evaluation(child, moves)
                        child.visits += 1
                        self.backpropagation(child, reward)
                        break
                if leaf.visits > len(leaf.children):
                    leaf.is_expanded = True
        distribution = np.zeros(len(self.root_node.state) - 1)
        for child in self.root_node.children:
            distribution[child.action[0]] = child.visits
        print("Dist:", distribution)
        distribution = distribution / sum(distribution)
        self.RBUF.append((self.root_node.state, distribution))
        if len(self.RBUF) > 2000:
            self.RBUF.reverse()
            new_buff = self.RBUF[:2000]
            save_RBUF(self.RBUF[2000:], self.size)
            self.RBUF = new_buff
            self.RBUF.reverse()
        #print(time.time() - start)
        #print("Tree search: {:.2}s. \nExpansion: {:.2}s. \nEvaluation: {:2f}s. \nBackpropagation {:.2}s. \nTraining {:.2}s ".format(*self.time))

        return distribution.argmax()

    def tree_search(self):
        """ Traversing the tree from the root to a leaf node by using the tree policy

        :return: (Node, moves from root to leaf.)
        """
        start = time.time()
        node = self.root_node
        node.visits += 1
        minmax = True
        moves = 0
        is_expanded = node.is_expanded

        if get_best_child(node, True).is_final_state:
            child = get_best_child(node, True)
            child.visits += 1
            return child, 1

        while is_expanded is True:
            node = get_best_child(node, minmax)
            node.visits += 1
            is_expanded = node.is_expanded
            minmax = True if minmax is False else False
            moves += 1
        self.time[0] += time.time()-start
        return node, moves

    def expansion(self, leaf):
        """ Generating some or all child states of a parent state, and then connecting the tree
            node housing the parent state (a.k.a. parent node) to the nodes housing the child states (a.k.a. child
            nodes)

        :param leaf: Node, the node that is to be expanded
        """
        start = time.time()
        children = self.game_manager.get_child_action_pair(leaf.state)
        leaf.children = [Node(state, action) for state, action in children]
        for child in leaf.children:
            child.parent = leaf
            leaf.q_values[child.action] = 0
            if self.game_manager.is_win(child.state):
                child.is_final_state = True
        self.time[1] += time.time() - start

    def evaluation(self, leaf, moves, epsilon=0.2):
        """ Estimating the value of a leaf node in the tree by doing a rollout simulation using
            the default policy from the leaf node’s state to a final state.

        :param leaf: Node, to be evaluated
        :param moves: int, number of moves from root to finish node
        :return: int, reward
        """
        s = time.time()
        t = np.zeros(5)
        state = copy.deepcopy(leaf.state)
        while not self.game_manager.is_win(state):
            start = time.time()
            rand_int = random.randint(0,9)
            actions = self.game_manager.get_actions(state)
            if rand_int >= epsilon*10:
                distribution = self.ANET.distribution(state)
                action = distibution_to_action(distribution, actions)
            else:
                action = actions[random.randint(0,len(actions)-1)]
            state = self.game_manager.do_action(state, action)
            moves += 1
        self.time[2] += time.time() - s
        return -1 if moves % 2 == 0 else 1/moves

    def backpropagation(self, leaf, reward):
        """ Passing the evaluation of a final state back up the tree, updating relevant data
            at all nodes and edges on the path from the final state to the tree root.

        :param leaf: Node, leaf node the rollout was from
        :param reward: int, reward to backpropagate
        """
        start = time.time()
        leaf.reward += reward
        node = leaf
        while node.parent:
            node.parent.reward += reward
            node.parent.q_values[node.action] = node.reward / node.visits
            node = node.parent
        self.time[3] += time.time() - start

    def get_action(self):
        """ Get the next action to be performed based on q_values

        :return: action to be performed
        """
        max_val = max(self.root_node.q_values.values())
        for action, value in self.root_node.q_values.items():
            if value == max_val:
                return action

    def set_new_root(self, state):
        """
        Function to set the new root and keep the children of the new root
        """
        v = [c.visits for c in self.root_node.children]
        #print("Root visits: ", v)
        for child in self.root_node.children:
            if child.state == state:
                self.root_node = child
                self.root_node.parent = None
                break

    def reset(self, state):
        """ Reset the root node to a given state

        :param state: state to be "noded"
        """
        self.root_node = Node(state, None)

    def train(self, g):
        """
        Method to train the neural net. This implementation only select one instance of a state (to avoid overfitting on rootnode).
        Implementation can be changed to include all states in RBUF by commenting out the if statement

        Also saving the NN for every g itteration
        """
        start = time.time()
        x_train = []
        y_train = []
        rbuf_copy = copy.deepcopy(self.RBUF)
        random.shuffle(rbuf_copy)
        for root, dist in rbuf_copy:
            x_train.append(copy.deepcopy(root))
            y_train.append(copy.deepcopy(dist))
        self.ANET.train(x_train, y_train)

        if (g+1) % self.save_interval == 0:
            self.ANET.save_model(g+1)
        elif g == 0:
            self.ANET.save_model(g)
        self.time[4] += time.time() - start


class Node:

    def __init__(self, state, action):
        """ Initialize a Node-object

        :param state: The state of the game in the Node
        :param action: The action that lead to this node
        """
        self.state = state
        self.children = []
        self.parent = None
        self.visits = 0
        self.action = action
        self.reward = 0
        self.is_expanded = False
        self.is_final_state = False
        self.q_values = {}


def get_best_child(node, max=True, c=1):
    """Finds the next Node to visit in the tree search based on max or min player.

    :param node: Node, current node
    :param max: Boolean, max or min node
    :return: Node, the best child
    """
    best_child = node.children[0]
    visits = np.log(node.visits)
    c = 2
    best_value = node.q_values[best_child.action] + c * np.sqrt(visits / (1 + best_child.visits))
    for child in node.children:
        if max:
            value = node.q_values[child.action] + c * np.sqrt(visits/(1 + child.visits))
            if value > best_value:
                best_value = value
                best_child = child
        elif not max:
            value = node.q_values[child.action] - c * np.sqrt(visits / (1 + child.visits))
            if value < best_value:
                best_value = value
                best_child = child
    return best_child


def distibution_to_action(distribution, actions):
    """
    Method to filter out the moves that isn't possible and returning the move with highest prob
    """
    a = [act[0] for act in actions]
    distribution = np.asarray([abs(d) for d in distribution])
    for i in range(distribution.size):
        if not a.__contains__(i):
            distribution[0][i] = 0
    return distribution.argmax(), actions[0][1]


def save_RBUF(RBUF, size):
    path = os.path.abspath('../Assignment3/RBUF/RBUF_' + str(size) + ".csv")
    file_obj = open(path, 'a', newline='')

    writer = csv.writer(file_obj, quoting=csv.QUOTE_ALL)

    for state, dist in RBUF:
        writer.writerow(state)
        writer.writerow(dist)
    file_obj.close()
