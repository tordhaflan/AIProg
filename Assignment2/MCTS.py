import random
import numpy as np


class MCTS:

    def __init__(self, game, state):
        """Init MCTS-object

        :param game:
        :param state:
        """
        self.game_manager = game
        self.root_node = Node(state, None)

    def simulate(self, m):
        """ Simulation of M different tree-searches to determine a move

        :param m: amount of simulations
        """
        self.expansion(self.root_node)
        for i in range(m):
            leaf, moves = self.tree_search()

            if self.game_manager.is_win(leaf.state):
                leaf.visits += 1
                reward = self.evaluation(leaf, moves)
                self.backpropagation(leaf, reward)
            elif len(leaf.children) == 0:
                self.expansion(leaf)
                child = leaf.children[random.randint(0, len(leaf.children)-1)-1]
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
                if leaf.visits == len(leaf.children) + 1:
                    leaf.is_expanded = True

    def tree_search(self):
        """ Traversing the tree from the root to a leaf node by using the tree policy

        :return: (Node, moves from root to leaf.)
        """
        leaf = False
        node = self.root_node
        node.visits += 1
        minmax = True
        moves = 0
        while leaf is not True:
            node = get_best_child(node, minmax)
            node.visits += 1
            leaf = not node.is_expanded
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
        if len(children) != 0:
            leaf.children = [Node(state, action) for state, action in children]
            for child in leaf.children:
                child.parent = leaf
                leaf.q_values[child.action] = 0
                if self.game_manager.is_win(child.state):
                    child.is_final_state = True
        else:
            leaf.is_final_state = True

    def evaluation(self, leaf, moves):
        """ Estimating the value of a leaf node in the tree by doing a rollout simulation using
            the default policy from the leaf node’s state to a final state.

        :param leaf: Node, to be evaluated
        :param moves: int, number of moves from root to finish node
        :return: int, reward
        """
        state = leaf.state
        while not self.game_manager.is_win(state):
            action = self.game_manager.get_random_action(state)
            state = self.game_manager.do_action(state, action)
            moves += 1

        return -1 if moves % 2 == 0 else 1

    def backpropagation(self, leaf, reward):
        """ Passing the evaluation of a final state back up the tree, updating relevant data
            at all nodes and edges on the path from the final state to the tree root.

        :param leaf: Node, leaf node the rollout was from
        :param reward: int, reward to backpropagate
        """
        leaf.reward += 1
        node = leaf
        while node.parent:
            node.parent.reward += reward
            node.parent.q_values[node.action] = node.reward/node.visits
            node = node.parent

    def get_action(self):
        """ Get the next action to be performed based on q_values

        :return: action to be performed
        """
        max_val = max(self.root_node.q_values.values())
        for action, value in self.root_node.q_values.items():
            if value == max_val:
                return action

    def reset(self, state):
        """ Reset the root node to a given state

        :param state: state to be "noded"
        """
        self.root_node = Node(state, None)


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


def get_best_child(node, max=True):
    """ Finds the next Node to visit in the tree search based on max or min player.

    :param node: Node, current node
    :param max: Boolean, max or min node
    :return: Node, the best child
    """
    best_child = node.children[0]
    visits = np.log(node.visits)
    best_value = node.q_values[best_child.action] + np.sqrt(visits / (1 + best_child.visits))
    for child in node.children:
        if max:
            value = node.q_values[child.action] + np.sqrt(visits/(1 + child.visits))
            if value > best_value:
                best_value = value
                best_child = child
        elif not max:
            value = node.q_values[child.action] - np.sqrt(visits / (1 + child.visits))
            if value < best_value:
                best_value = value
                best_child = child
    return best_child
