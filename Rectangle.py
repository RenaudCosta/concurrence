class Rectangle:

    def __init__(self, ox1, oy1, ox2, oy2):
        self.x1 = ox1
        self.y1 = oy1
        self.x2 = ox2
        self.y2 = oy2


    def isIn(self, x, y):
        return x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2