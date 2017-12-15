from tkinter import *
import time


class GroundDraw:
    def __init__(self, obstacles, persons):
        self.factor = 3
        self.window = Tk()
        self.canvas = self.create_canvas()
        self.draw_obstacles(obstacles)
        self.characterPosition = {}
        self.draw_persons(persons)
        self.draw_exit()
        self.canvas.pack()

    def update(self, person):
        time.sleep(0.01)
        self.canvas.delete(self.characterPosition[person.id])
        if not person.reach_exit():
            x = person.x
            y = person.y
            newRect = self.canvas.create_rectangle(x * self.factor, y * self.factor, (x + 1) * self.factor,
                                                   (y + 1) * self.factor,
                                                   fill='red')
            self.characterPosition[person.id] = newRect

    def create_canvas(self):
        longeur = 512 * self.factor
        largeur = 128 * self.factor
        return Canvas(self.window, width=longeur, height=largeur, background='gray')

    def draw_obstacles(self, obstacles):
        for i in range(0, len(obstacles), 1):
            obstacle = obstacles[i]
            self.canvas.create_rectangle(obstacle.x1 * self.factor, obstacle.y1 * self.factor,
                                         obstacle.x2 * self.factor, obstacle.y2 * self.factor, fill='black')

    def draw_persons(self, persons):
        for i in range(0, len(persons), 1):
            person = persons[i]
            x = person.x
            y = person.y
            newRect = self.canvas.create_rectangle(x * self.factor, y * self.factor, (x + 1) * self.factor,
                                                   (y + 1) * self.factor,
                                                   fill='red')
            self.characterPosition[person.id] = newRect

    def draw_exit(self):
        self.canvas.create_rectangle(0, 0, 6, 6, fill='green')

    def start(self):
        self.window.mainloop()
