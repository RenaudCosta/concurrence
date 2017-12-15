class Zone:
    def __init__(self, x, y, x2, y2):
        self.x = x
        self.x2 = x2
        self.y = y
        self.y2 = y2

    def contains(self, person):
        return self.x <= person.x <= self.x2 and self.y <= person.y <= self.y2

    def contient(self, x, y):
        return self.x <= x <= self.x2 and self.y <= y <= self.y2
