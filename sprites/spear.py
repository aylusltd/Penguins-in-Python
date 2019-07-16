import time
import sys

from os.path import dirname
from imp import load_source

import constants
import random
import string
from PIL import Image, ImageTk


# Preloading sound to memory
mypath = dirname(__file__)
temp_sound_path = 'sounds/punch.wav'
print('temp_sound_path')
print(temp_sound_path)
Sound = load_source('Sound', mypath+'/../Classes/Sound.py').Sound
my_sound = Sound(temp_sound_path)
my_sound.load()

class Spear(constants.correction):
    def __init__(self,app, d=0, x=None, y=None):
        int(d)
        self.sound = my_sound
        # self.sound.load()
        self.pause = False
        self.app = app
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        cx = w/(2*g)
        cy = h/(2*g)-1
        if x is not None:
            cx=x
        if y is not None:
            cy=y
        img = Image.open("sprites/sm_spear.gif")
        if d is not 0:
            img = img.rotate(d, expand=True)
        self.m_sprite = ImageTk.PhotoImage(img)
        self.sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.m_sprite)
        self.row=cy
        self.column=cx
        self.app.spears.append(self)
        self.d=d
        self.valid=True
        self.move()

    def destroy(self):
        print("Destroying Spear")
        # print self.app.spears.index(self)
        self.app.spears.remove(self)
        self.valid = False
        self.app.screen.canvas.delete(self.sprite)
        del self

    def move(self):
        if not self.valid:
            return None
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        max_row = int(h/g)-2
        max_column = int(w/g)-2
        if self.d == 0 and not self.pause:
            # up
            self.row-=1
            if self.row < 0:
                self.destroy()
            else:
                self.app.screen.canvas.move(self.sprite,0,-g)
        if self.d == 180 and not self.pause:
            # down
            self.row+=1
            if self.row > max_row:
                self.destroy()
            else:
                self.app.screen.canvas.move(self.sprite,0,g)
        if self.d == 90 and not self.pause:
            # left
            self.column-=1
            if self.column < 0:
                self.destroy()
            else:
                self.app.screen.canvas.move(self.sprite,-g,0)
        if self.d == 270 and not self.pause:
            # right
            self.column+=1
            if self.column > max_column:
                self.destroy()
            else:
                self.app.screen.canvas.move(self.sprite,g,0)
        if not self.pause:
            c=False
            # try:
            #     c = self.detect_collision()
            # except:
            #     print("row")
            #     print(self.row)
            #     print("column")
            #     print(self.column)
            c = self.detect_collision()
            if c:
                self.destroy()
        self.app.root.after(constants.INTERVAL,self.move)

    # def __del__(self):
    #     print "deleting"
    #     print self.row
    #     print self.column

    def detect_collision(self):
        self.pause = True
        # print("Row")
        # print(self.row)
        # print("column")
        # print(self.column)
        if self.app.screen.grid[self.row][self.column].occupied:
            for monster in self.app.screen.monsters:
                if monster.row == self.row and monster.column == self.column:
                    monster.hit(1)
                    self.sound.play()
                    # time.sleep(10)
                    # del monster
                    # print("monster")
                    return True
            self.pause = False
            return False
        self.pause = False
        return False