import random

import numpy as np


class MCTS:

    def __init__(self, game, state):
        self.game_manager = game
        # self.game_manager = Game(['Ledge', 100, 50, 1, [0, 1, 0, 0, 1, 1, 2, 1, 0, 1, 0, 1, 1], False])
        self.root_node = Node(state, None)

    def simulate(self, m):
        self.expansion(self.root_node)
        for i in range(m):
            leaf = self.tree_search()
            if leaf.is_final_state:
                reward = self.evaluation(leaf)
                self.backpropagation(leaf, reward)
            elif len(leaf.children) == 0:
                self.expansion(leaf)
                child = leaf.children[random.randint(0, len(leaf.children)-1)-1]
                reward = self.evaluation(child)
                child.visits += 1
                self.backpropagation(child, reward)
            else:
                for child in leaf.children:
                    if child.visits == 0:
                        reward = self.evaluation(child)
                        child.visits += 1
                        self.backpropagation(child, reward)
                        break
                if leaf.visits == len(leaf.children) + 1:
                    leaf.is_expanded = True


    def tree_search(self):
        leaf = False
        node = self.root_node
        node.visits += 1
        minmax = True
        while leaf is not True:
            node = get_best_child(node, minmax)
            node.visits += 1
            leaf = not node.is_expanded
            minmax = True if minmax == False else False

        return node

    # Implementation of an expansion
    # Finne ut hvor vi holder styr på .visits
    # Funker ikke helt enda, barna har samme state som parent.
    def expansion(self, leaf):
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

    # Implementation of rollout
    # As of now, we dont add the random path and therefor will not backpropagate this path (only from the leaf node and up)
    def evaluation(self, leaf):
        state = leaf.state
        number_of_moves = 0
        while not self.game_manager.is_win(state):
            number_of_moves += 1
            action = self.game_manager.get_random_action(state)
            state = self.game_manager.do_action(state, action)

        return 1 if number_of_moves % 2 == 0 else -1

    def backpropagation(self, leaf, reward):
        node = leaf
        while node.parent:
            node.reward += reward
            node.parent.reward += reward
            node.parent.q_values[node.action] = node.parent.reward/node.visits
            node = node.parent

    def get_action(self):
        max_val = max(self.root_node.q_values.values())
        for action, value in self.root_node.q_values.items():
            if value == max_val:
                return action


# Endret til Node for å få bedre oversikt selv og for å slippe State.state.
class Node:

    def __init__(self, state, action):
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
    best_child = node.children[0]
    best_value = node.q_values[best_child.action] + np.sqrt(np.log(node.visits) / (1 + best_child.visits))
    for child in node.children:
        if max:
            value = node.q_values[child.action] + np.sqrt(np.log(node.visits) / (1 + child.visits))
            if value > best_value:
                best_value = value
                best_child = child
        elif not max:
            value = node.q_values[child.action] - np.sqrt(np.log(node.visits) / (1 + child.visits))
            if value < best_value:
                best_value = value
                best_child = child
    return best_child
