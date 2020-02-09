class Critic:

    #  Initialize Critic-object
    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        """
        :param learning_rate: Input from parameters.txt
        :param eligibility_rate: Input from parameters.txt
        :param discount_factor: Input from parameters.txt
        """
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}
        self.delta = 0

    #  Calculate TD-error. Delta = reward if in goal state.
    def calculate_delta(self, reward, next_state, state):
        if next_state is None:
            self.delta = reward
        else:
            self.delta = reward + self.discount_factor * self.values[next_state] - self.values[state]

    #  Update state-value based on formula: V(s) ← V(s)+ αcδe(s)
    def change_value(self, state):
        self.values[state] = self.values[state] + self.learning_rate * self.delta * self.eligibilities[state]

    #  Update eligibility value based on formula: e(s) ← γλe(s)
    def update_eligibility(self, state, previous_state):
        self.eligibilities[state] = self.discount_factor * self.eligibility_rate * self.eligibilities[previous_state]

