from Person import *
from Obstacle import *
from GroundDraw import *
from Personne import *


def simulation(nbPersons):
    obstacles = createObstacles()


def createObstacles():
    obstacle1 = Obstacle(50, 30, 100, 60)
    obstacle2 = Obstacle(100, 90, 105, 110)
    obstacle3 = Obstacle(200, 10, 205, 40)
    obstacle4 = Obstacle(210, 45, 260, 90)
    obstacle5 = Obstacle(300, 40, 400, 115)
    return [obstacle1, obstacle2, obstacle3, obstacle4, obstacle5]


def createPersonnes():
    personne = Personne(0, 0)
    personne2 = Personne(50, 50)
    personne3 = Personne(200, 10)
    return [personne, personne2, personne3]


obstacles = createObstacles()
personnes = createPersonnes()
draw = GroundDraw(obstacles, personnes)
