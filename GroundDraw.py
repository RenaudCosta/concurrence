from tkinter import *


class GroundDraw:
    def __init__(self, obstacles, personnes):
        self.window = Tk()
        self.obstacles = obstacles
        longeur = 512
        largeur = 128
        self.canvas = Canvas(self.window, width=longeur, height=largeur, background='gray')

        for i in range(0, len(obstacles), 1):
            obstacle = obstacles[i]
            self.canvas.create_rectangle(obstacle.x1, obstacle.y1, obstacle.x2, obstacle.y2, fill = 'black')

        for i in range(0,len(personnes),1):
            personne = personnes[i]
            x = personne.x
            y = personne.y
            self.canvas.create_rectangle(x,y,x+3,y+3, fill = 'red')

        self.canvas.pack()
        self.window.mainloop()

    def update(self, arg):
        return arg