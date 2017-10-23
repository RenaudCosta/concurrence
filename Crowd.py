#!/usr/bin/python
from Person import *
from Obstacle import *
from GroundDraw import *
from Settings import *
import _thread
import sys
from random import randint
import time

def move(thread_id, persons, obstacles, draw):
    while True:
        person = persons[thread_id]
        if person.y == 0:
            if not isInObstacle(person.x-1, 0, obstacles):
                person.x -= 1
        elif person.x == 0:
            if not isInObstacle(0, person.y-1, obstacles):
                person.y -= 1
        else:
            if isInObstacle(person.x-1, person.y-1, obstacles):
                if not isInObstacle(person.x, person.y-1, obstacles):
                    person.y -= 1
                elif not isInObstacle(person.x-1, person.y, obstacles):
                    person.x -= 1
            else:
                person.y -= 1
                person.x -= 1
        if draw != 0:
            draw.update(person)

def simulation(settings):
    nbPersons = pow(2, int(settings.persons))
    obstacles = createObstacles()
    persons = createPersons(nbPersons, obstacles)
    threads = []

    startingTime = time.clock()
    if not settings.metrics:
        draw = GroundDraw(obstacles, persons)
    else:
        draw = 0


    if settings.mode == "0":
        for i in range(nbPersons):
            threads.append(_thread.start_new_thread(move, (i,persons,obstacles,draw,)))
    elif settings.mode == 1:
        for i in range(4):
            # TODO
            threads.append(_thread.start_new_thread())
            print("TODO")
    draw.start()


    # After the simulation is over
    execTime = time.clock() - startingTime

    if settings.metrics:
        return execTime


def isInObstacle(x, y, obstacles):
    for obs in obstacles:
        if x >= obs.x1 and x <= obs.x2:
            if y >= obs.y1 and y <= obs.y2:
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

    #remove exit as an availible spot
    spots.remove([0, 0])
    spots.remove([0, 1])
    spots.remove([1, 0])
    spots.remove([1, 1])

    for n in range(nbPersons):
        index = randint(0, len(spots))
        newX = spots[index][0]
        newY = spots[index][1]
        while isInObstacle(newX, newY, obstacles):
            index = randint(0, len(spots))
            newX = spots[index][0]
            newY = spots[index][1]
        person = Person(newX, newY, n+1)
        del spots[index]
        persons.append(person)

    return persons

def generateSettings():
    t, p, m = 0, 4, False
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i][0] == "-":
                if sys.argv[i][1] == "t":
                    t = sys.argv[i][2]
                elif sys.argv[i][1] == "p":
                    p = sys.argv[i][2]
                elif sys.argv[i][1] == "m":
                    m = True
    return Settings(t, p, m)


settings = generateSettings()
if settings.metrics:
    execTimes = []
    for i in range(5):
        execTimes.append(simulation(settings))
    execTimes.remove(max(execTimes))
    execTimes.remove(min(execTimes))
    average = (execTimes[0]+execTimes[1]+execTimes[2])/3
    print("Execution time: " + str(average)[0:8] + "s")
else:
    simulation(settings)