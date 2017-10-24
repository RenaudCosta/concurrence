class Grid:
    def __init__(self, personages):
        self.occupied_array = [[False for i in range(128)] for j in range(512)]
        for person in personages:
            x, y = person.x, person.y
            self.occupied_array[x][y] = True

    def remove_occupation(self, person):
        self.occupied_array[person.x][person.y] = False

    def set_occupation(self, person):
        self.occupied_array[person.x][person.y] = True
