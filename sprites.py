import random
import string
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

from PIL import Image, ImageTk
from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu, Canvas
import yaml

# Why do these not work"    
# from sprites.spear import Spear
# from sprites.Fish import Fish
# from sprites.Monster import Monster
# When this does?
from Classes.Screen import Screen
from Classes.Sprite import Sprite

import constants
import maps


mypath = dirname(__file__)
Spear = load_source('Spear', mypath+'/sprites/Spear/Spear.py').Spear

Fish = load_source('Fish', mypath+'/sprites/Fish/Fish.py').Fish
Monster = load_source('Monster', mypath+'/sprites/Monster/Monster.py').Monster
Tux = load_source('Tux', mypath+'/sprites/Tux/Tux.py').Tux

class Fire(Sprite):
    def __init__(self,app, x, y):
        self.life = 10
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        cx = x
        cy = y
        img = Image.open("sprites/Items/sm_fire.gif")
        self.f_sprite = ImageTk.PhotoImage(img)
        self.sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.f_sprite)
        self.row=y
        self.column=x
        self.app = app

        app.screen.fires.append(self)
        app.sprites.append(self)
    
    def on_clock_tick(self, tick):
        self.life -= 1
        if self.life <= 0:
            self.destroy()

    def destroy(self):
        app = self.app
        screen = app.screen
        canvas = screen.canvas
        fires = app.screen.fires
        sprites = app.sprites
        canvas.delete(self.sprite)
        fires.remove(self)
        sprites.remove(self)


class Tree(Sprite):
    def __init__(self, app, x, y, g=constants.grid_size):
        self.row=y
        self.column=x
        self.app = app
        pass

    def on_clock_tick(self, tick):
        if tick % 50 == 0:
            pass
        neighbor = app.screen.neighbor_has(feature="tree", i=self.row,j=self.column)

def Trees(app):
    h = constants.bounds["y"][1]
    w = constants.bounds["x"][1]
    g = constants.grid_size
    img = Image.open("sprites/Tiles/sm_tree.gif")
    img.thumbnail((g,g))
    app.t_sprite = ImageTk.PhotoImage(img)

    for row in app.screen.grid:
        for s in row:
            r = random.randint(0,12)
            start_cluster= r < 2
            continue_cluster= r < 8
            neighbor = app.screen.neighbor_has(feature="tree", i=s.row,j=s.column)
            if ((start_cluster or (continue_cluster and neighbor)) and s.square_type == "grass" and not s.occupied):
                s.add_feature("tree", app)

def Rocks(app):
    h = constants.bounds["y"][1]
    w = constants.bounds["x"][1]
    g = constants.grid_size
    img = Image.open("sprites/Tiles/sm_rock.gif")
    img.thumbnail((g,g))
    app.r_sprite = ImageTk.PhotoImage(img)

    for row in app.screen.grid:
        for s in row:
            r = random.randint(0,12)
            start_cluster= r == 0
            continue_cluster= r < 5
            neighbor = app.screen.neighbor_has(feature="rock", i=s.row,j=s.column)
            if ((start_cluster or (continue_cluster and neighbor)) and s.square_type == "grass" and not s.occupied):
                s.add_feature("rock", app)

