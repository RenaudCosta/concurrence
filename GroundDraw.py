from tkinter import *


class GroundDraw:
    def __init__(self, obstacles, persons):
        self.factor = 3
        self.window = Tk()
        self.createCanvas()
        self.drawObstacles(obstacles)
        self.drawPersons(persons)
        self.drawExit()
        self.canvas.pack()
        self.window.mainloop()

    def update(self, arg):
        return arg

    def createCanvas(self):
        longeur = 512 * self.factor
        largeur = 128 * self.factor
        self.canvas = Canvas(self.window, width=longeur, height=largeur, background='gray')

    def drawObstacles(self, obstacles):
        for i in range(0, len(obstacles), 1):
            obstacle = obstacles[i]
            self.canvas.create_rectangle(obstacle.x1 * self.factor, obstacle.y1 * self.factor,
                                         obstacle.x2 * self.factor, obstacle.y2 * self.factor, fill='black')

    def drawPersons(self, persons):
        for i in range(0, len(persons), 1):
            personne = persons[i]
            x = personne.x
            y = personne.y
            self.canvas.create_rectangle(x * self.factor, y * self.factor, (x + 1) * self.factor, (y + 1) * self.factor,
                                         fill='red')

    def drawExit(self):
        self.canvas.create_rectangle(0, 0, 6, 6, fill='green')
