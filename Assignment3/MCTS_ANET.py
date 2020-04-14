import random
import copy
import numpy as np
from Assignment3.MCTS import Node, get_best_child
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

    def simulate(self, m):
        """ Simulation of M different tree-searches to determine a move

        :param m: amount of simulations
        """
        self.expansion(self.root_node)
        for i in range(m):
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
        distribution = distribution / sum(distribution)
        self.RBUF.append((self.root_node.state, distribution))

        return distribution.argmax()

    def tree_search(self):
        """ Traversing the tree from the root to a leaf node by using the tree policy

        :return: (Node, moves from root to leaf.)
        """
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
        return node, moves

    def expansion(self, leaf):
        """ Generating some or all child states of a parent state, and then connecting the tree
            node housing the parent state (a.k.a. parent node) to the nodes housing the child states (a.k.a. child
            nodes)

        :param leaf: Node, the node that is to be expanded
        """
        children = self.game_manager.get_child_action_pair(leaf.state)
        leaf.children = [Node(state, action) for state, action in children]
        for child in leaf.children:
            child.parent = leaf
            leaf.q_values[child.action] = 0
            if self.game_manager.is_win(child.state):
                child.is_final_state = True

    def evaluation(self, leaf, moves, epsilon=0.1):
        """ Estimating the value of a leaf node in the tree by doing a rollout simulation using
            the default policy from the leaf node’s state to a final state.

        :param leaf: Node, to be evaluated
        :param moves: int, number of moves from root to finish node
        :return: int, reward
        """
        state = copy.deepcopy(leaf.state)
        while not self.game_manager.is_win(state):
            rand_int = random.randint(0,9)
            actions = self.game_manager.get_actions(state)
            distribution = self.ANET.distribution(state)
            if rand_int >= epsilon*10:
                action = distibution_to_action(distribution, actions)
            else:
                action = actions[random.randint(0,len(actions)-1)]
            state = self.game_manager.do_action(state, action)
            moves += 1
        return -1 if moves % 2 == 0 else 1

    def backpropagation(self, leaf, reward):
        """ Passing the evaluation of a final state back up the tree, updating relevant data
            at all nodes and edges on the path from the final state to the tree root.

        :param leaf: Node, leaf node the rollout was from
        :param reward: int, reward to backpropagate
        """
        leaf.reward += reward
        node = leaf
        while node.parent:
            node.parent.reward += reward
            node.parent.q_values[node.action] = node.reward / node.visits
            node = node.parent

    def get_action(self):
        """ Get the next action to be performed based on q_values

        :return: action to be performed
        """
        max_val = max(self.root_node.q_values.values())
        for action, value in self.root_node.q_values.items():
            if value == max_val:
                return action

    def set_new_root(self, state):
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
        x_train = []
        y_train = []
        for root, dist in self.RBUF:
            x_train.append(root)
            y_train.append(dist)
        self.ANET.train(x_train, y_train)

        if (g+1) % self.save_interval == 0:
            self.ANET.save_model(g+1)
        elif g == 0:
            self.ANET.save_model(g)


def distibution_to_action(distribution, actions):
    a = [act[0] for act in actions]
    #TODO
    # Check this up
    distribution = np.asarray([abs(d) for d in distribution])
    for i in range(distribution.size):
        if not a.__contains__(i):
            distribution[0][i] = 0
    return distribution.argmax(), actions[0][1]
