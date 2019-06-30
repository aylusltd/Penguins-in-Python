import random
import string
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu
from PIL import Image, ImageTk

import constants
class Square(constants.correction):
    def debug_click(self, event):
        DEBUG_MODE = True
        row = int(event.y/constants.grid_size)
        column = int(event.x/constants.grid_size)
        s = self.app.screen.grid[row][column]
        
        if DEBUG_MODE:
            o = string.Template('Clicked {x:$column, y:$row}').substitute({'column':column, 'row': row})
            print(o)
            print("Type: " + s.square_type)
            print("Passable: " +str(s.passable))
            print("Occupied: " + str(s.occupied))
            print("Has Tux: " + str(s.has_tux))
            print("Has Wall: " + str(s.has_wall))
            print("Has Fish: " + str(s.has_fish))
            print(str(self.sprites))

        action = self.app.action
        if action is not None:
            print(action)
            # def remove_feature(self, feature, app, make_passable=True):
            if action == "destroy wall":
            	s.remove_feature(feature="wall", app=self.app)
            elif action == "catch fish":
            	print("in catch routine")
            	for fish in self.app.screen.fishes:
	                if fish.row == s.row and fish.column == s.column:
	                    fish.destroy()
	                    del fish
	                    self.app.inventory["fish"]["qty"]+=10
	                    self.app.update_inventory()
	                    print("caught fish")

            self.app.action = None
            # self.app.config(cursor = "arrow black black")


    def __init__(self, row, column, canvas, app, g=constants.grid_size, square_type='grass'):
        if canvas is not None:
            self.canvas = canvas
            if square_type == 'grass':
                fill='green'
                self.passable=True
            elif square_type == 'water':
                fill='blue'
                self.passable = False
            self.representation = canvas.create_rectangle(
                (column*g)+5, 
                (row*g)+5, 
                ((column+1)*g)+5, 
                ((row+1)*g)+5,
                fill=fill)
            self.canvas.bind("<Button-1>", self.debug_click)
            self.canvas.bind("<Control-Button-1>", app.edit_square)
        self.square_type = square_type
        self.row=row
        self.column=column
        self.app = app
        self.occupied=False
        self.has_tree = False
        self.has_rock = False
        self.has_tux = False
        self.has_wall = False
        self.has_fish = False
        self.sprites={}
    
    def add_feature(self, feature, app, required_type="grass", passable=True):
        g = constants.grid_size
        img = Image.open("sprites/sm_"+feature+".gif")
        img.thumbnail((g,g))
        name = feature+"_sprite"
        # print name
        if name not in app.sprites:
            app.sprites[feature+"_sprite"] = ImageTk.PhotoImage(img)
        prop = "has_" + feature
        if (self.square_type == required_type and not self.occupied):
                self.sprites[feature+"_sprite"] = app.screen.canvas.create_image(((self.column+0.5)*g)+5, ((self.row+0.5)*g)+5, image=app.sprites[feature+"_sprite"])                    
                self[prop]=True
                self.passable = passable
        # print str(self)
    def remove_feature(self, feature, app, make_passable=True):
        # print "Remove Feature"
        # g = constants.grid_size
        name = feature+"_sprite"
        # print name
        prop = "has_" + feature
        # grid[i][j]
        touching_wall = app.screen.neighbor_has(feature="tux", i=self.row, j=self.column)
        # print "Touching Wall:"
        # print touching_wall
        # print ""
        if (touching_wall and self[prop]):
                self[prop] = False
                self.passable = make_passable
                self.app.screen.canvas.delete(self.sprites[feature+"_sprite"])

