import random
import string
from os.path import dirname

from tkinter import Canvas
import yaml

import constants
import maps

from Classes.Square import Square

mypath = dirname(__file__)

class Screen(constants.correction):
    def __init__(self,app, height=constants.bounds["y"][1], width=constants.bounds["x"][1], grid=constants.grid_size):
        self.h=height
        self.g=grid
        self.w=width
        self.monsters = []
        self.fishes = []
        self.fires = []

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
        self.app.sprites=None
        self.app.sprites=[]
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
                    
                    else:
                        square_type = 'grass'
                if self.current_map["x"] == 0 and j==0:
                    square_type = 'water'
                if self.current_map["y"] == 0 and i==0:
                    square_type = 'water'

                try:
                    s = Square(i,j, self.canvas, app=self.app, square_type=square_type)
                except:
                    print("r=", r)
                    raise Exception("Boom")
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
