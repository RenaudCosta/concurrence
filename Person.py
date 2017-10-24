from random import randint


class Person:
    def __init__(self, px, py, id):
        self.x = px
        self.y = py
        self.id = id

    def reach_exit(self):
        return self.x <= 1 and self.y <= 1
