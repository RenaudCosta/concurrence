#!/usr/bin/python
from Person import *
from Rectangle import *
from GroundDraw import *
from Settings import *
import sys
from random import randint
import time
from threading import Lock, Thread
import psutil
import copy

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


def move_persons(thread_id, obstacles, zones, zonesPersons, draw):
    for z in range(len(zonesPersons)):
        for p in zonesPersons[z]:
            if isOnRightEdge(p.x, zones):
                print("lock")
                lockBorders[z][p.y].acquire()

    while len(zonesPersons[thread_id]) > 0:
        rnd = 0
        person = zonesPersons[thread_id][rnd]

        if person.reach_exit():
            zonesPersons[thread_id].remove(person)
        else:
            #release previous lock if needed
            if isOnLeftEdge(person.x, zones):
                lockBorders[thread_id][person.y].release()
                make_person_move_t1(obstacles, person, zonesPersons, zones)
            elif isOnRightEdge(person.x, zones) and thread_id > 0:
                lockBorders[thread_id-1][person.y].acquire()
                person.x -= 1
            else:
                make_person_move_t1(obstacles, person, zonesPersons, zones)

            if draw != 0:
                draw.update(person)

        # check changing zone
        if not zones[thread_id].isIn(person.x, person.y):
            tempPerson = copy.copy(person)
            zonesPersons[thread_id].remove(person)
            zonesPersons[thread_id - 1].append(tempPerson)


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
        zonesPersons = initZonesPersons(persons, zones)
        lockCases(persons)
        for i in range(4):
            threads.append(Thread(target=move_persons, args=(i, obstacles, zones, zonesPersons, draw,)))
            threads[i].start()

    if not settings.metrics:
        draw.start()

    # After the simulation is over
    execTime = time.clock() - startingTime

    if settings.metrics:
        return [execTime, psutil.cpu_percent(interval=None)]


def initZonesPersons(persons, zones):
    zonesPersons = [[] for i in range(4)]
    for p in persons:
        for i in range(len(zones)):
            if zones[i].isIn(p.x, p.y):
                zonesPersons[i].append(p)
    return zonesPersons

def lockCases(persons):
    for p in persons:
        lockMatrix[p.x][p.y].acquire()


def isInObstacle(x, y, obstacles):
    for obs in obstacles:
        if obs.isIn(x, y):
            return True
    return False

def isOnRightEdge(x, zones):
    return (getZone(x, zones) != getZone(x-1, zones))

def isOnLeftEdge(x, zones):
    return (getZone(x, zones) != getZone(x+1, zones))

def getZone(x, zones):
    for i in range(len(zones)):
        if zones[i].isIn(x, 1):
            return i
    return -1

def createObstacles():
    obstacle1 = Rectangle(50, 30, 100, 60)
    obstacle2 = Rectangle(100, 90, 105, 110)
    obstacle3 = Rectangle(200, 10, 205, 40)
    obstacle4 = Rectangle(210, 45, 240, 90)
    obstacle5 = Rectangle(300, 40, 400, 115)
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


def make_person_move_t1(obstacles, person, zonesPersons, zones):
    zoneId = getZone(person.x, zones)
    zone = zonesPersons[zoneId]
    if person.y == 0:
        if not isInObstacle(person.x - 1, 0, obstacles): # Move West
            if isFree(person.x-1, person.y, zone):
                person.x -= 1
    elif person.x == 0:
        if not isInObstacle(0, person.y - 1, obstacles): # Move North
            if isFree(person.x, person.y-1, zone):
                person.y -= 1
    else:
        if isInObstacle(person.x - 1, person.y - 1, obstacles):
            if not isInObstacle(person.x, person.y - 1, obstacles):
                if isFree(person.x, person.y-1, zone):
                    person.y -= 1
            elif not isInObstacle(person.x - 1, person.y, obstacles):
                if isFree(person.x-1, person.y, zone):
                    person.x -= 1
        else: # Move NW
            if lockMatrix[person.x-1][person.y-1].locked() and lockMatrix[person.x-2][person.y-2].locked(): # If NW already taken, let's try West, then North
                if not isInObstacle(person.x - 1, 0, obstacles):
                    if isFree(person.x-1, person.y, zone):
                        person.x -= 1
                elif not isInObstacle(person.x, person.y - 1, obstacles):
                    if isFree(person.x, person.y-1, zone):
                        person.y -= 1
            else:
                if isFree(person.x-1, person.y-1, zone):
                    person.y -= 1
                    person.x -= 1

def isFree(x, y, persons):
    for p in persons:
        if p.x == x and p.y == y:
            return False
    return True

global lockMatrix
global lockBorders
global zones
lockMatrix = [[Lock() for k in range(128)] for j in range(512)]
lockBorders = [[Lock() for k in range(128)] for j in range(3)]

zones = [Rectangle(0, 0, 127, 127), Rectangle(128, 0, 255, 127), Rectangle(256, 0, 383, 127),
                 Rectangle(384, 0, 511, 127)]
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