from Person import *
from Obstacle import *
from GroundDraw import *
from Personne import *

from random import randint

def simulation(nbPersons):
    obstacles = createObstacles()
    persons = createPersons(10, obstacles)

def createObstacles():
    obstacle1 = Obstacle(50, 30, 100, 60)
    obstacle2 = Obstacle(100, 90, 105, 110)
    obstacle3 = Obstacle(200, 10, 205, 40)
    obstacle4 = Obstacle(210, 45, 240, 90)
    obstacle5 = Obstacle(300, 40, 400, 115)
    return [obstacle1, obstacle2, obstacle3, obstacle4, obstacle5]

def createPersons(nbPersons, obstacles):
    persons = []
    spots = []
    for y in range(128):
        for x in range(256):
                spots.append([x, y])

    for obs in obstacles:
        for y in range(obs.y1, obs.y2+1):
            for x in range(obs.x1, obs.x2+1):
                if [x, y] in spots:
                    spots.remove([x, y])

    for n in range(nbPersons):
        index = randint(0, len(spots))
        person = Person(spots[index][0], spots[index][1])
        del spots[index]
        persons.append(person)

    return persons

obstacles = createObstacles()
personnes = createPersons(10, obstacles)
draw = GroundDraw(obstacles, personnes)


simulation(64)