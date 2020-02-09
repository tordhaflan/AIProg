class Actor:

    #  Initialize Actor-object
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

    #  Sets SAP-values if state is not visited before.
    def set_values(self, state, actions):
        for action in actions:
            self.values[state + action] = 0

    #  Update SAP-values according to formula Π(s,a) ← Π(s,a) +αaδe(s,a)
    def change_value(self, state, action, delta):
        self.values[state + action] = self.values[state + action] \
                                    + self.learning_rate * delta * self.eligibilities[state + action]

    # Updates e based on formula e(s,a) ← γλe(s,a)
    def update_eligibility(self, state, action, previous_state, previous_action):
        self.eligibilities[state + action] = self.discount_factor * self.eligibility_rate \
                                             * self.eligibilities[previous_state + previous_action]
