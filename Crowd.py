#!/usr/bin/python
from Person import *
from Obstacle import *
from GroundDraw import *
from Settings import *
import sys
from random import randint
import time
from threading import Lock, Thread
import psutil

def move(thread_id, persons, obstacles, draw):
    reach_exit = False
    person = persons[thread_id]
    lockMatrix[person.x][person.y].acquire()
    while not reach_exit:
        if person.reach_exit():
            reach_exit = True
        else:
            make_person_move(obstacles, person)
            if draw != 0:
                draw.update(person)


def move_persons(thread_id, persons, obstacles, draw):
    print("donothing")


def simulation(settings):
    nbPersons = pow(2, int(settings.persons))
    obstacles = createObstacles()
    persons = createPersons(nbPersons, obstacles)

    startingTime = time.clock()
    psutil.cpu_percent(interval=None) # 1st call
    if not settings.metrics:
        draw = GroundDraw(obstacles, persons)
    else:
        draw = 0

    threads = []

    if settings.mode == "0":
        for i in range(nbPersons):
            threads.append(Thread(target=move, args=(i, persons, obstacles, draw,)))
            threads[i].start()
    elif settings.mode == "1":
        for i in range(4):
            threads.append(Thread(target=move_persons, args=(i, persons, obstacles, draw,)))
            threads[i].start()

    if not settings.metrics:
        draw.start()

    # After the simulation is over
    execTime = time.clock() - startingTime

    if settings.metrics:
        return [execTime, psutil.cpu_percent(interval=None)]


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

    # remove exit as an availible spot
    spots.remove([0, 0])
    spots.remove([0, 1])
    spots.remove([1, 0])
    spots.remove([1, 1])

    for n in range(nbPersons):
        index = randint(0, len(spots)-1)
        newX = spots[index][0]
        newY = spots[index][1]
        while isInObstacle(newX, newY, obstacles):
            index = randint(0, len(spots))
            newX = spots[index][0]
            newY = spots[index][1]
        person = Person(newX, newY, n + 1)
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

def make_person_move(obstacles, person):
    if person.y == 0:
        if not isInObstacle(person.x - 1, 0, obstacles): # Move West
            lockMatrix[person.x-1][0].acquire()
            person.x -= 1
            lockMatrix[person.x+1][0].release()
    elif person.x == 0:
        if not isInObstacle(0, person.y - 1, obstacles): # Move North
            lockMatrix[0][person.y-1].acquire()
            person.y -= 1
            lockMatrix[0][person.y+1].release()
    else:
        if isInObstacle(person.x - 1, person.y - 1, obstacles):
            if not isInObstacle(person.x, person.y - 1, obstacles):
                lockMatrix[person.x][person.y-1].acquire()
                person.y -= 1
                lockMatrix[person.x][person.y+1].release()
            elif not isInObstacle(person.x - 1, person.y, obstacles):
                lockMatrix[person.x-1][person.y].acquire()
                person.x -= 1
                lockMatrix[person.x+1][person.y].release()
        else: # Move NW
            if lockMatrix[person.x-1][person.y-1].locked() and lockMatrix[person.x-2][person.y-2].locked(): # If NW already taken, let's try West, then North
                if not isInObstacle(person.x - 1, 0, obstacles):
                    lockMatrix[person.x-1][person.y].acquire()
                    person.x -= 1
                    lockMatrix[person.x+1][person.y].release()
                elif not isInObstacle(person.x, person.y - 1, obstacles):
                    lockMatrix[person.x][person.y-1].acquire()
                    person.y -= 1
                    lockMatrix[person.x][person.y+1].release()
            else:
                lockMatrix[person.x-1][person.y-1].acquire()
                person.y -= 1
                person.x -= 1
                lockMatrix[person.x+1][person.y+1].release()
    if person.reach_exit():
        lockMatrix[person.x][person.y].release()


global lockMatrix
lockMatrix = [[Lock() for k in range(128)] for j in range(512)]
settings = generateSettings()
if settings.metrics:
    execTimes = []
    cpuUsages = []
    for i in range(5):
        metrics = simulation(settings)
        execTimes.append(metrics[0])
        cpuUsages.append(metrics[1])

    execTimes.remove(max(execTimes))
    execTimes.remove(min(execTimes))
    cpuUsages.remove(max(cpuUsages))
    cpuUsages.remove(min(cpuUsages))
    averageTime = (execTimes[0] + execTimes[1] + execTimes[2]) / 3
    averageCPU = (cpuUsages[0] + cpuUsages[1] + cpuUsages[2]) / 3
    print("Average execution time: " + str(averageTime)[0:8] + "s")
    print("Average CPU Usage: " + str(averageCPU)[0:5] + "%")
else:
    simulation(settings)