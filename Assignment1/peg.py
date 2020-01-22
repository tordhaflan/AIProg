class Peg(object):

    def __init__(self, x, y, number, filled=True):
        self.coordinates = (x,y)
        self.neighbours = []
        self.filled = filled
        self.pegNumber = number

    def set_neighbours(self, neighbours):
        for n in neighbours:
            self.neighbours.append(n)
