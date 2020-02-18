class Actor:

    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        """ Initialize Actor-object

        :param learning_rate: Input from parameters.txt
        :param eligibility_rate: Input from parameters.txt
        :param discount_factor: Input from parameters.txt
        """
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}

    def set_values(self, state, actions):
        """ Sets SAP-values

        :param state: current state
        :param actions: possible actions
        """
        for action in actions:
            self.values[state + action] = 0

    def change_value(self, state, action, delta):
        """ Update SAP-values according to formula Π(s,a) ← Π(s,a) +αaδe(s,a)

        :param state: current state
        :param action: one action
        :param delta:
        :return:
        """
        self.values[state + action] = self.values[state + action] \
            + self.learning_rate * delta * self.eligibilities[state + action]

    def reset_eligibilities(self):
        """ Resets eligibilities to 0
        """
        for key in self.eligibilities.keys():
            self.eligibilities[key] = 0

    def update_eligibility(self, state, action):
        """ Updates e based on formula e(s,a) ← γλe(s,a)

        :param state: current state
        :param action: one action
        """
        self.eligibilities[state + action] = self.discount_factor * self.eligibility_rate \
                                             * self.eligibilities[state + action]
