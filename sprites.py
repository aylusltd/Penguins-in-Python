import random
import string
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

from PIL import Image, ImageTk
from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu, Canvas

import constants

mypath = dirname(__file__)
Spear = load_source('Spear', mypath+'/sprites/spear.py').Spear
Square = load_source('Square', mypath+'/Classes/Square.py').Square
Fish = load_source('Fish', mypath+'/sprites/Fish.py').Fish


class Sprite(constants.correction):
    def __init__(self,app, x=None, y=None):
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        cx = int(w/(2*g))
        cy = int(h/(2*g))
        img = Image.open("sprites/sm_tux.gif")
        self.p_sprite = ImageTk.PhotoImage(img)
        self.row=cy
        self.column=cx
        original_cx = cx

        s=app.screen.grid[cy][cx]
        tries=0
        if (x is None) or (y is None):
            while (s.square_type != 'grass') and (tries < 20):
                # constants.l('Moving from {x:$x, y:$y}', {'x':cx,'y':cy})
                if cx>0:
                    cx-=1
                else:
                    cx=original_cx
                    cy-=1
                tries+=1
                s=app.screen.grid[cy][cx]
            if tries == 20:
                app.screen=Screen(app)
        else:
            cx = x
            cy = y


        self.sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.p_sprite)
        app.screen.grid[cy][cx].occupied=True
        app.screen.grid[cy][cx].has_tux=True
        self.app = app

    def hit(self,damage):
        print("Hit")
        fish = self.app.inventory["fish"]["qty"]
        if fish >= damage:
            self.app.inventory["fish"]["qty"]-=damage
            self.app.update_inventory()
        else:
            print("Oh No")

class Monster(constants.correction):
    def __init__(self,app, x=None, y=None):
        # constants.l('Placing Monster',{})
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size

        cx = int(w/(2*g))+random.randint(1,5)
        cy = int(h/(2*g))+random.randint(-4,4)
        img = Image.open("sprites/sm_monster.gif")

        self.m_sprite = ImageTk.PhotoImage(img)
        original_cx = cx
        s=app.screen.grid[cy][cx]
        tries=0
        MAX_TRIES = 30
        if (x is None) or (y is None):
            while (s.passable is False or s.occupied is True) and (tries < MAX_TRIES):
                # constants.l('Moving from {x:$x, y:$y}', {'x':cx,'y':cy})
                if cx<(w/g)-2:
                    cx+=random.randint(0,2)
                # else:
                    # cx=original_cx
                    cy+=random.randint(-2,2)
                tries+=1
                s=app.screen.grid[cy][cx]

        else:
            cx = x
            cy = y
        if tries < MAX_TRIES:
            s=app.screen.grid[cy][cx]
            self.sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.m_sprite)
            self.row=cy
            self.column=cx
            s.occupied=True
            self.app = app
            self.type = "virus"
            self.placed = True
        else: 
            print("Tries exceeded")
            self.placed = False
    def destroy(self):
        self.app.screen.canvas.delete(self.sprite)
        self.app.screen.grid[self.row][self.column].occupied = False
        self.app.screen.monsters.remove(self)
    
    # def __del__(self):
    #     print "deleting monster"
    #     print self.row
    #     print self.column

def Trees(app):
    h = constants.bounds["y"][1]
    w = constants.bounds["x"][1]
    g = constants.grid_size
    img = Image.open("sprites/sm_tree.gif")
    img.thumbnail((g,g))
    app.t_sprite = ImageTk.PhotoImage(img)

    for row in app.screen.grid:
        for s in row:
            r = random.randint(0,12)
            start_cluster= r< 3
            continue_cluster= r < 9
            neighbor = app.screen.neighbor_has(feature="tree", i=s.row,j=s.column)
            if ((start_cluster or (continue_cluster and neighbor)) and s.square_type == "grass" and not s.occupied):
                s.add_feature("tree", app)

def Rocks(app):
    h = constants.bounds["y"][1]
    w = constants.bounds["x"][1]
    g = constants.grid_size
    img = Image.open("sprites/sm_rock.gif")
    img.thumbnail((g,g))
    app.r_sprite = ImageTk.PhotoImage(img)

    for row in app.screen.grid:
        for s in row:
            r = random.randint(0,12)
            start_cluster= r== 0
            continue_cluster= r < 5
            neighbor = app.screen.neighbor_has(feature="rock", i=s.row,j=s.column)
            if ((start_cluster or (continue_cluster and neighbor)) and s.square_type == "grass" and not s.occupied):
                s.add_feature("rock", app)
                # s.rock_sprite = app.screen.canvas.create_image(((s.column+0.5)*g)+5, ((s.row+0.5)*g)+5, image=app.r_sprite)                    
                # s.has_rock=True

class Screen(constants.correction):
    def __init__(self,app, height=constants.bounds["y"][1], width=constants.bounds["x"][1], grid=constants.grid_size):
        h=height
        g=grid
        w=width
        self.canvas=Canvas(app.frame, height=h+10, width=w+10, background="green")
        self.grid = []
        for i in range(0,(int(h/g))):
            self.grid.append([])
            # print app.grid[i]
            for j in range(0,(int(w/g))):
                r = random.randint(0,12)
                if r%11 == 0:
                    square_type = 'water'
                elif r%4 ==0 and self.neighbor_water(i,j):
                    square_type = 'water'
                else:
                    square_type = 'grass'
                s = Square(i,j, self.canvas, app=app, square_type=square_type)
                self.grid[i].append(s)
    
    def neighbor_has(self, feature, i,j):
        prop = "has_"+feature
        # debug_feature = ["wall", "tux"]
        debug_feature = []
        # Remember range is broken and checks from min to max - 1
        for x in range(-1,2):
            for y in range(-1,2):
                nx = j+x
                ny = i+y
                if feature in debug_feature:
                    o = string.Template('Checking {x:$column, y:$row}').substitute({'column':nx, 'row': ny})
                    print(o)
                    print(prop + ": " + str(self.grid[ny][nx][prop]))
                try:
                    if self.grid[ny][nx][prop] == True:
                        if feature in debug_feature:
                            print("Found neighbor")
                        return True
                except IndexError:
                    if feature in debug_feature:
                        print("Out of range")
                    else:
                        pass
        return False
    def neighbor_water(self, i,j):
        for x in range(-1,1):
            for y in range(-1,1):
                try:
                    if self.grid[i+y][j+x].square_type == 'water':
                        return True
                except IndexError:
                    pass

    def save(self):
        arr = []
        for row in self.grid:
            save_row = []
            for square in row:
                save_row.append()
            arr.append(save_row)

