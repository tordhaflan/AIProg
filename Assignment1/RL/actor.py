class Actor:

    #  Initialisere Actor-objekt
    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}

    #  Setter nye verdier for SAP dersom staten ikke er besøkt fra før
    def set_values(self, state, actions):
        for action in actions:
            self.values[state + action] = 0

    #  Oppdaterer SAP-value
    def change_value(self, state, action, delta):
        self.values[state + action] = self.values[state + action] \
                                    + self.learning_rate * delta * self.eligibilities[state + action]

    #  Oppdaterer eligibility value, kun på best path, skjer etter end state er oppnådd
    def update_eligibility(self, state, action, previous_state, previous_action):
        self.eligibilities[state + action] = self.discount_factor * self.eligibility_rate \
                                             * self.eligibilities[previous_state + previous_action]
