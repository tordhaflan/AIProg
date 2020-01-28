class Peg(object):

    def __init__(self, x, y, row, col, number,  filled=True):
        self.drawing_coordinates = (x,y)
        self.coordinates = (row, col)
        self.neighbours = []
        self.filled = filled
        self.pegNumber = number

    def set_neighbours(self, neighbours):
        for n in neighbours:
            self.neighbours.append(n)
