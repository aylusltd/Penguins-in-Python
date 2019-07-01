import random
import string
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

from PIL import Image, ImageTk
from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu, Canvas

import constants
import maps

mypath = dirname(__file__)
Spear = load_source('Spear', mypath+'/sprites/spear.py').Spear
Square = load_source('Square', mypath+'/Classes/Square.py').Square
Fish = load_source('Fish', mypath+'/sprites/Fish.py').Fish

class Sprite(constants.correction):
    pass

class Tux(Sprite):
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

    def hit(self, damage):
        print("Hit")
        fish = self.app.inventory["fish"]["qty"]
        if fish >= damage:
            self.app.inventory["fish"]["qty"]-=damage
            self.app.update_inventory()
        else:
            print("Oh No")

class Monster(Sprite):
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
                try:
                    s=app.screen.grid[cy][cx]
                except IndexError:
                    print("Out of range")
                    self.placed = False
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
            start_cluster= r < 2
            continue_cluster= r < 8
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
            start_cluster= r == 0
            continue_cluster= r < 5
            neighbor = app.screen.neighbor_has(feature="rock", i=s.row,j=s.column)
            if ((start_cluster or (continue_cluster and neighbor)) and s.square_type == "grass" and not s.occupied):
                s.add_feature("rock", app)

class Screen(constants.correction):
    def __init__(self,app, height=constants.bounds["y"][1], width=constants.bounds["x"][1], grid=constants.grid_size):
        self.h=height
        self.g=grid
        self.w=width
        self.monsters = []
        self.fishes = []

        self.canvas=Canvas(app.frame, height=self.h+10, width=self.w+10, background="green")
        self.grid = []
        self.grids = []
        self.app = app
        for i in range(0,20):
            self.grids.append([])
            for j in range(0,20):
                self.grids[i].append({})
        self.current_map = {}
        self.current_map["x"] = random.randint(0,19)
        self.current_map["y"] = random.randint(0,19)
        app.starting_map = self.current_map.copy()

        for i in range(0,(int(self.h/self.g))):
            self.grid.append([])
            # print app.grid[i]
            for j in range(0,(int(self.w/self.g))):
                r = random.randint(0,12)
                if r%11 == 0:
                    square_type = 'water'
                elif r%4 ==0 and self.neighbor_type(i,j, square_type='water'):
                    square_type = 'water'
                else:
                    square_type = 'grass'
                s = Square(i,j, self.canvas, app=app, square_type=square_type)
                self.grid[i].append(s)
        
        y = self.current_map["y"]
        x = self.current_map["x"]
    
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
    def neighbor_type(self, i,j, square_type='water'):
        for x in range(-1,1):
            for y in range(-1,1):
                try:
                    if self.grid[i+y][j+x].square_type == square_type:
                        return True
                except IndexError:
                    pass


    def generate_screen(self, from_dir):
        self.canvas.delete("all")
        self.app.screen.monsters=None
        self.app.screen.monsters=[]
        self.app.screen.fishes=None
        self.app.screen.fishes=[]
        print('generate_screen')
        print(self.app.screen.fishes)
        # print(self)
        g = self.grid.copy()
        # delete(self.grid)

        h = len(g)
        w = len(g[0])
        # m = self.monsters.copy()
        # f = self.fishes.copy()
        new_grid=[]
        for i in range(0,h):
            new_grid.append([])
            for j in range(0,w):
                if from_dir == "Down" and i==0:
                    source_square=g[-1][j]
                    square_type=source_square.square_type
                elif from_dir == "Up" and i==h-1:
                    source_square=g[0][j]
                    square_type=source_square.square_type
                elif from_dir == "Left" and j==w-1:
                    source_square=g[i][0]
                    square_type=source_square.square_type
                elif from_dir == "Right" and j==0:
                    source_square=g[i][-1]
                    square_type=source_square.square_type
                else:
                    r = random.randint(0,12)
                    if r%11 == 0:
                        square_type = 'water'
                    elif r%12 == 1:
                        if abs(self.current_map["y"]-self.app.starting_map["y"]) > 10 or self.current_map["y"] < 5:
                            square_type = 'snow'
                        elif abs(self.current_map["y"]-self.app.starting_map["y"]) < 10:
                            square_type = 'sand'

                    elif r%4 ==0:
                        if self.neighbor_type(i,j, square_type='water'):
                            square_type = 'water'
                        elif self.neighbor_type(i,j, square_type='snow'):
                            square_type = 'snow'
                        elif self.neighbor_type(i,j, square_type='sand'):
                            square_type = 'sand'
                    
                    else:
                        square_type = 'grass'
                if self.current_map["x"] == 0 and j==0:
                    square_type = 'water'
                if self.current_map["y"] == 0 and i==0:
                    square_type = 'water'

                s = Square(i,j, self.canvas, app=self.app, square_type=square_type)
                new_grid[i].append(s)

        return new_grid
    def make_next_screen(self, direction, tux_x, tux_y):
        print(self.current_map)
        x = self.current_map["x"]
        y = self.current_map["y"]

        self.grids[y][x]=maps.save(app=self.app, in_memory=True)

        if direction == "Up":
            y -=1
        elif direction == "Down":
            y+=1
        elif direction == "Right":
            x+=1
        elif direction == "Left":
            x-=1
        
        self.current_map["y"] = y
        self.current_map["x"] = x

        m=self.grids[y][x]

        if "grid" in m:
            maps.load(app=self.app, from_memory=m)
        else:
            new_grid = self.generate_screen(direction)
            self.grid = new_grid.copy()
            self.grids[y][x]["grid"] = new_grid.copy()
            self.app.add_sprites(tux_x=tux_x,tux_y=tux_y, monsters=[], fishes=[])
