class Critic:

    #  Initialisere Critic-objekt
    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}
        self.delta = 0

    #  Regne ut TD-error, hvis i goal-state, TD-error = reward
    def calculate_delta(self, reward, next_state, state):
        if next_state is None:
            self.delta = reward
        else:
            self.delta = reward + self.discount_factor * self.values[next_state] - self.values[state]

    #  Oppdatere state-value
    def change_value(self, state):
        self.values[state] = self.values[state] + self.learning_rate * self.delta * self.eligibilities[state]

    #  Oppdatere eligibility value
    def update_eligibility(self, state, previous_state):
        self.eligibilities[state] = self.discount_factor * self.eligibility_rate * self.eligibilities[previous_state]

