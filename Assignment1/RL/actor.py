class Actor:

    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}

    def change_value(self, state, action, delta):
        self.values[state + action] = self.values[state + action] \
                                    + self.learning_rate * delta * self.eligibilities[state + action]

    def update_eligibility(self, state, action, previous_state, previous_action):
        self.eligibilities[state + action] = self.discount_factor * self.eligibility_rate \
                                             * self.eligibilities[previous_state + previous_action]
