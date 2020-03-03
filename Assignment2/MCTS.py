class MCTS:

    def __init__(self, game):
        self.game_manager = game
        # self.game_manager = Game(['Ledge', 100, 50, 1, [0, 1, 0, 0, 1, 1, 2, 1, 0, 1, 0, 1, 1], False])
        self.root_node = Node(self.game_manager.get_initial_state(), True)
        self.current_node = self.root_node

    def simulate(self, m):
        #For m
            #Kjør en tree_search
            #Expansion og
        pass

    def tree_search(self):
        pass

    # Implementation of an expansion
    # Finne ut hvor vi holder styr på .visits
    # Funker ikke helt enda, barna har samme state som parent.
    def expansion(self, leaf):
        if not leaf.is_expanded and not leaf.is_final_state:
            leaf.children = [Node(state, action) for state, action in self.game_manager.get_child_action_pair(leaf.state)]
            for child in leaf.children:
                child.parent = leaf
            leaf.is_expanded = True


    # Implementation of rollout
    # As of now, we dont add the random path and therefor will not backpropagate this path (only from the leaf node and up)
    def evaluation(self, leaf):
        state = leaf.state
        number_of_moves = 0
        while not self.game_manager.is_win(state):
            number_of_moves += 1
            action = self.game_manager.get_random_action(state)
            state = self.game_manager.do_action(state, action)

        if not number_of_moves % 2 == 0:
            leaf.parent.q_values[leaf.parent.action] = -1
        else:
            leaf.parent.q_values[leaf.parent.action] = 1



    def backpropagation(self, path):
        pass

    def get_action(self, state):
        value = 0
        best_action = None
        best_node = None
        for child in self.current_node:
            if max(child.q_values().values()) > value:
                value = max(child.q_values().values())
                best_action = child.action
                best_node = child
        self.current_node = best_node
        return best_action

    #TODO
    # Her må også current_node settes til root_node!
    def reset_values(self):
        pass


# Endret til Node for å få bedre oversikt selv og for å slippe State.state.
class Node:

    def __init__(self, state, action, root=False):
        self.state = state
        self.children = []
        self.parent = None
        self.visits = 0
        self.action = action
        self.root = root
        self.is_expanded = False
        self.is_final_state = False
        self.q_values = {}

