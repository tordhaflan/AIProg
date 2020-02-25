

class MCTS:

    def __init__(self):
        pass

    def simulate(self):
        pass

    def tree_search(self):
        pass

    def expansion(self):
        pass

    #Implementation of rollout
    def evaluation(self):
        pass

    def backpropagation(self):
        pass

class State:

    def __init__(self):
        self.children = []
        self.parent = []
        self.visits = 0
        self.player = 1
        self.is_final_state = False
