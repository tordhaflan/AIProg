class Actor:

    def __init__(self, learning_rate, eligibility_rate, discount_factor):
        self.learning_rate = learning_rate
        self.eligibility_rate = eligibility_rate
        self.discount_factor = discount_factor

        self.values = {}
        self.eligibilities = {}
