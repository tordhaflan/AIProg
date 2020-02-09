class Peg(object):

    # Initialize Peg-object
    def __init__(self, x, y, row, col, number,  filled=True):
        """
        :param x: x-coordinate
        :param y: y-coordinate
        :param row: row-number
        :param col: row-number
        :param number: peg-number
        :param filled: if peg is filled or not
        """
        self.drawing_coordinates = (x, y)
        self.coordinates = (row, col)
        self.neighbours = []
        self.filled = filled
        self.pegNumber = number

    # Appends neighbouring peg to the list of neighbours
    def set_neighbours(self, neighbours):
        for n in neighbours:
            self.neighbours.append(n)
