#!/usr/bin/python
from threading import Lock, Thread

import psutil

from Zone import *
from GroundDraw import *
from Obstacle import *
from Person import *
from Settings import *


######################## Partie Scenario 1 ###############################


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


def make_person_move(obstacles, person):
    if person.y == 0:
        if not isInObstacle(person.x - 1, 0, obstacles):  # Move West
            lockMatrix[person.x - 1][0].acquire()
            person.x -= 1
            lockMatrix[person.x + 1][0].release()
    elif person.x == 0:
        if not isInObstacle(0, person.y - 1, obstacles):  # Move North
            lockMatrix[0][person.y - 1].acquire()
            person.y -= 1
            lockMatrix[0][person.y + 1].release()
    else:
        if isInObstacle(person.x - 1, person.y - 1, obstacles):
            if not isInObstacle(person.x, person.y - 1, obstacles):
                lockMatrix[person.x][person.y - 1].acquire()
                person.y -= 1
                lockMatrix[person.x][person.y + 1].release()
            elif not isInObstacle(person.x - 1, person.y, obstacles):
                lockMatrix[person.x - 1][person.y].acquire()
                person.x -= 1
                lockMatrix[person.x + 1][person.y].release()
        else:  # Move NW
            if lockMatrix[person.x - 1][person.y - 1].locked() and lockMatrix[person.x - 2][
                        person.y - 2].locked():  # If NW already taken, let's try West, then North
                if not isInObstacle(person.x - 1, 0, obstacles):
                    lockMatrix[person.x - 1][person.y].acquire()
                    person.x -= 1
                    lockMatrix[person.x + 1][person.y].release()
                elif not isInObstacle(person.x, person.y - 1, obstacles):
                    lockMatrix[person.x][person.y - 1].acquire()
                    person.y -= 1
                    lockMatrix[person.x][person.y + 1].release()
            else:
                lockMatrix[person.x - 1][person.y - 1].acquire()
                person.y -= 1
                person.x -= 1
                lockMatrix[person.x + 1][person.y + 1].release()
    if person.reach_exit():
        lockMatrix[person.x][person.y].release()


#################### Partie scenario 2 ###############################

global foule_par_zone
foule_par_zone = [[] for i in range(4)]

global barrieres
barrieres = [[Lock() for k in range(128)] for j in range(3)]

global zones
zones = []


def creer_zone():
    decal = 512 / 4
    decal = int(decal)
    for i in range(4):
        zones.append(Zone(i * decal, 0, (i + 1) * decal, 128))


def ajouter_foule_par_zone(zones, persons):
    for zone_id in range(len(zones)):
        zone = zones[zone_id]
        for person in persons:
            if zone.contains(person):
                foule_par_zone[zone_id].append(person)


def initialiser_barriere():
    decal = 512 / 4
    for foule_id in range(len(foule_par_zone)):
        for personne in foule_par_zone[foule_id]:
            if personne.x == decal - 1:
                barrieres[0][personne.y].acquire()
            elif personne.x == decal * 2 - 1:
                barrieres[1][personne.y].acquire()
            elif personne.x == decal * 3 - 1:
                barrieres[2][personne.y].acquire()


def initialisation(persons):
    for i in range(len(barrieres)):
        for j in range(len(barrieres[i])):
            if barrieres[i][j].locked():
                barrieres[i][j].release()
    while len(zones) > 0:
        del zones[0]
    creer_zone()
    ajouter_foule_par_zone(zones, persons)
    initialiser_barriere()


def move_persons(thread_id, obstacles, draw):
    personne_index = 0
    nombre_personne = 0
    for i in range(len(foule_par_zone)):
        for j in range(len(foule_par_zone[i])):
            nombre_personne += 1
    while nombre_personne != 0:
        if len(foule_par_zone[thread_id]) != 0:
            personnage = foule_par_zone[thread_id][personne_index]
            a_bouger_ou_finis_ou_changer_zone = fait_bouger_personne(personnage, obstacles,
                                            thread_id, draw)
            if not a_bouger_ou_finis_ou_changer_zone and len(foule_par_zone[thread_id])-1 > personne_index:
                personne_index += 1
            elif not a_bouger_ou_finis_ou_changer_zone:
                personne_index = 0
            nb_personne = 0
            for i in range(len(foule_par_zone)):
                for j in range(len(foule_par_zone[i])):
                    nb_personne += 1
            nombre_personne = nb_personne


def is_someone(x, y, thread_id):
    for personne in foule_par_zone[thread_id]:
        if personne.x == x and personne.y == y:
            return True
    return False


def est_dans_la_bonne_zone(x_haut_gauche, y_haut_gauche, thread_id):

    return zones[thread_id].contient(x_haut_gauche + 2, y_haut_gauche) or zones[thread_id].contient(x_haut_gauche,
                                                                                                    y_haut_gauche + 2) or \
           zones[thread_id].contient(x_haut_gauche + 2, y_haut_gauche + 2)


def aller_haut_gauche(personne):
    personne.x -= 1
    personne.y -= 1


def verifie_la_direction(x_haut_gauche, y_haut_gauche, thread_id, obstacles):
    if x_haut_gauche < 0 or y_haut_gauche < 0:
        return False
    if is_someone(x_haut_gauche, y_haut_gauche, thread_id):
        return False
    if isInObstacle(x_haut_gauche, y_haut_gauche, obstacles):
        return False
    if not est_dans_la_bonne_zone(x_haut_gauche, y_haut_gauche, thread_id):
        return False
    return True


def aller_gauche_possible(personne, obstacles, thread_id):
    x_haut_gauche = personne.x - 1
    y_haut_gauche = personne.y
    return verifie_la_direction(x_haut_gauche, y_haut_gauche, thread_id, obstacles)


def aller_haut_gauche_possible(personne, obstacles, thread_id):
    x_haut_gauche = personne.x - 1
    y_haut_gauche = personne.y - 1
    return verifie_la_direction(x_haut_gauche, y_haut_gauche, thread_id, obstacles)


def aller_gauche(personne):
    personne.x -= 1


def aller_haut_possible(personne, obstacles, thread_id):
    x_haut_gauche = personne.x
    y_haut_gauche = personne.y - 1
    return verifie_la_direction(x_haut_gauche, y_haut_gauche, thread_id, obstacles)


def aller_haut(personne):
    personne.y -= 1


def position_fait_partie_barriere(x_position):
    return x_position == 128 - 1 or x_position == 256 - 1 or x_position == 256 + 128 - 1


def pas_de_personnes_autre_thread(thread_id, x, y):
    for perso in foule_par_zone[thread_id]:
        if x == perso.x and y == perso.y:
            return False
    return True


def fait_bouger_personne(personne, obstacles, thread_id, draw):
    x_precedent = personne.x
    y_precedent = personne.y
    if aller_haut_gauche_possible(personne, obstacles, thread_id) and pas_de_personnes_autre_thread(thread_id - 1,
                                                                                                    personne.x - 1,
                                                                                                    personne.y - 1):
        aller_haut_gauche(personne)
    elif aller_gauche_possible(personne, obstacles, thread_id) and pas_de_personnes_autre_thread(thread_id - 1,
                                                                                                 personne.x - 1,
                                                                                                 personne.y):
        aller_gauche(personne)
    elif aller_haut_possible(personne, obstacles, thread_id):
        aller_haut(personne)
    else:
        return False
    if draw != 0:
        draw.update(personne)
    if personne.reach_exit():
        foule_par_zone[thread_id].remove(personne)
        return False
    if position_fait_partie_barriere(personne.x):
        if not position_fait_partie_barriere(x_precedent):
            foule_par_zone[thread_id].remove(personne)
            foule_par_zone[thread_id - 1].append(personne)
        barrieres[thread_id - 1][personne.y].acquire()
        return False
    if position_fait_partie_barriere(x_precedent) and barrieres[thread_id][y_precedent].locked():
        barrieres[thread_id][y_precedent].release()
    return True


def essai_transfert_personne_autre_zone(personne):
    pass


#################### Partie commune aux 2 ############################

def isInObstacle(x, y, obstacles):
    for obs in obstacles:
        if obs.x1 <= x <= obs.x2:
            if obs.y1 <= y <= obs.y2:
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
    spots.remove([0, 0])
    spots.remove([0, 1])
    spots.remove([1, 0])
    spots.remove([1, 1])
    for n in range(nbPersons):
        index = randint(0, len(spots) - 1)
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


################### Lancement ########################################





def simulation(settings):
    nbPersons = pow(2, int(settings.persons))
    obstacles = createObstacles()
    persons = createPersons(nbPersons, obstacles)

    startingTime = time.clock()
    psutil.cpu_percent(interval=None)  # 1st call
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
        initialisation(persons)
        for i in range(4):
            threads.append(Thread(target=move_persons, args=(i, obstacles, draw,)))
            threads[i].start()

    if not settings.metrics:
        draw.start()

    # After the simulation is over
    execTime = time.clock() - startingTime

    if settings.metrics:
        return [execTime, psutil.cpu_percent(interval=None)]


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
