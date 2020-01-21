class Peg(object):

    def __init__(self, x, y, number, neighbours=[], filled=True):
        self.coordinates = (x,y)
        self.neighbours = neighbours
        self.filled = filled
        self.pegNumber = number

    def set_neighbours(self, neighbours):
        [self.neighbours.append(n) for n in neighbours]




