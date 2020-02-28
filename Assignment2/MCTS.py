from Assignment2.game import Game

class MCTS:

    def __init__(self):
        self.game_manager = Game()
        # self.game_manager = Game(['Ledge', 100, 50, 1, [0, 1, 0, 0, 1, 1, 2, 1, 0, 1, 0, 1, 1], False])
        self.root_node = Node(self.game_manager.get_initial_state(), True)

    def simulate(self):
        pass

    def tree_search(self):
        pass

    # Implementation of an expansion
    # Finne ut hvor vi holder styr på .visits
    # Funker ikke helt enda, barna har samme state som parent.
    def expansion(self, leaf):
        if not leaf.is_expanded and not leaf.is_final_state:
            children_states = self.game_manager.get_child_states() # Dette funker seff ikke, skal se videre på det
            leaf.children = [Node(state) for state in children_states]
            for child in leaf.children:
                child.parent = leaf
            leaf.is_expanded = True


    # Implementation of rollout
    # As of now, we dont add the random path and therefor will not backpropagate this path (only from the leaf node and up)
    def evaluation(self, leaf, path):
        state = leaf.state
        while not self.game_manager.is_win():
            action = self.game_manager.get_random_action()
            state = self.game_manager.do_action(action)

    def backpropagation(self, path):
        pass


# Endret til Node for å få bedre oversikt selv og for å slippe State.state.
class Node:

    def __init__(self, state, root=False):
        self.state = state
        self.children = []
        self.parent = None
        self.visits = 0
        self.root = root
        self.is_expanded = False
        self.is_final_state = False
        self.q_values = {}

