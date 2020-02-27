from Assignment2.game import Game

class MCTS:

    def __init__(self):
        self.game_manager = Game()
        self.root_node = State(self.game_manager.get_initial_state(), True)

    def simulate(self):
        pass

    def tree_search(self):
        pass

    def expansion(self):
        pass

    # Implementation of rollout
    # As of now, we dont add the random path and therefor will not backpropagate this path (only from the leaf node and up)
    def evaluation(self, leaf, path):
        state = leaf.state
        while not self.game_manager.is_win():
            action = self.game_manager.get_random_action()
            state = self.game_manager.do_action(action)


    def backpropagation(self, path):
        pass

class State:

    def __init__(self, state, root=False):
        self.state = state
        self.children = []
        self.parent = None
        self.visits = 0
        self.root = root
        self.is_expanded = False
        self.is_final_state = False
        self.q_values = {}

