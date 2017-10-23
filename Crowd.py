#!/usr/bin/python
from Person import *
from Obstacle import *
from GroundDraw import *
from threading import Thread

from random import randint

def simulation(nbPersons):
    obstacles = createObstacles()
    persons = createPersons(nbPersons, obstacles)
    draw = GroundDraw(obstacles, persons)

def isInObstacle(x, y, obstacles):
    for obs in obstacles:
        if x > obs.x1 and x < obs.x2:
            if y > obs.y1 and y < obs.y2:
                return True
    return False

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
        for x in range(512):
                spots.append([x, y])

    for n in range(nbPersons):
        index = randint(0, len(spots))
        newX = spots[index][0]
        newY = spots[index][1]
        while isInObstacle(newX, newY, obstacles):
            index = randint(0, len(spots))
            newX = spots[index][0]
            newY = spots[index][1]
        person = Person(newX, newY)
        del spots[index]
        persons.append(person)

    return persons

simulation(16)