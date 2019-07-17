from os.path import isfile, join, realpath, abspath, dirname

from PIL import Image, ImageTk
import yaml

import constants
from constants import grid_size as g
import maps

from Classes.Sprite import Sprite

class Tux(Sprite):
    moving = False
    rest_fill_per_tick = 2 #equivalent to needing to sleep 8 hours per day
    resting = False
    resting_metabolic_rate = 0.5
    wake_distance = 2
    def __init__(self,app, x=None, y=None):
        self.moving = False
        g = constants.grid_size
        # self.snore_img = Image.open("sprites/Tux/snore.gif")
        self.snore_frames = [Image.open("sprites/Tux/snore/snore-%i.gif" %(i)) for i in range(4)]
        for index, frame in enumerate(self.snore_frames):
            frame.thumbnail((1.5*g,1.5*g), Image.ANTIALIAS)
            self.snore_frames[index] = ImageTk.PhotoImage(frame)
        self.snore_frame = 0
        self.state={}
        with open("configs/tux.yaml", 'r') as stream:
            try:
                self.state = yaml.safe_load(stream)
                # print starting_inventory
            except yaml.YAMLError as exc:
                print(exc)
        self.attributes = self.state["attributes"]
        self.state = self.state["stats"]
        state = self.state
        for stat in state:
            state[stat]["max"]=state[stat]["qty"]
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        cx = int(w/(2*g))
        cy = int(h/(2*g))
        img = Image.open("sprites/Tux/sm_tux.gif")
        self.img = img
        self.sprite = ImageTk.PhotoImage(img)
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

        self.canvas = app.screen.canvas
        self.canvas_sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.sprite)
        app.screen.grid[cy][cx].occupied=True
        app.screen.grid[cy][cx].has_tux=True
        self.app = app

    def increment_stat(self, stat, qty, over_max=False):
        self.state[stat]["qty"]+=qty
        if not over_max:
            self.state[stat]["qty"] = min(self.state[stat]["qty"], self.state[stat]["max"])

    def update_snore_sprite(self):
        g = constants.grid_size
        # img = Image.open("sprites/snore.gif")
        cy = self.row
        cx = self.column
        # self.snore_sprite = ImageTk.PhotoImage(img)
        
        try:
            self.app.screen.canvas.delete(self.snore_sprite)
        except:
            pass
        self.snore_frame+=1
        self.snore_frame = self.snore_frame % len(self.snore_frames)
        self.snore_sprite = self.app.screen.canvas.create_image(((cx+1.5)*g)+5, ((cy-0.5)*g)+5, image=self.snore_frames[self.snore_frame])

    def rest(self):
        print("sleep")
        self.resting = True
    
    def wake(self):
        print("wake")
        if self.resting:
            self.app.screen.canvas.delete(self.snore_sprite)
            self.resting = False

    def hit(self, damage):
        print("Hit")
        health = self.state["health"]["qty"]
        # fish = self.app.inventory["fish"]["qty"]
        if health >= damage:
            self.state["health"]["qty"]-=damage
            # self.app.update_inventory()
        else:
            print("Oh No")

    def move(self, direction):
        if self.moving == True:
            return None
        s = self.app
        delta = maps.move(direction, 1)
        g = constants.grid_size
        if s.screen.grid[s.tux.row+delta["y"]][s.tux.column + delta["x"]].passable:
            self.animate_move(direction)

    def round_pos(self, digits=0):
        self.row=round(self.row, digits)
        self.column=round(self.column, digits)
        if digits==0:
            self.row = int(self.row)
            self.column = int(self.column)

    def update_pos(self, delta, original_row, original_column):
        square = self.app.screen.grid[original_row][original_column]
        square.has_tux = False
        square.occupied = False

        self.round_pos()
        square = self.app.screen.grid[self.row][self.column]
        square.has_tux = True
        square.occupied = True
        canvas = self.canvas
        canvas.delete(self.canvas_sprite)
        cx = self.column
        cy = self.row
        self.canvas_sprite = canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.sprite)
        self.moving = False

    def animate_move(self, direction, d=0, r=None, original_row=None,original_column=None):
        self.moving = True
        
        g = constants.grid_size
        delta = maps.move(direction, 1)
        PACE = 10
        g = g/PACE
        d+=1
        if r is None:
            r = PACE-1
            original_row = self.row
            original_column = self.column
        angle = 20
        if d % 2 == 1:
            angle = -20
        if 0 == r:
            angle = 0
        self.row+= delta["y"]/PACE
        self.column+= delta["x"]/PACE
        self.round_pos(1)
        self.rotate_sprite(angle)
        self.canvas.move(self.canvas_sprite,g*delta["x"],g*delta["y"])
        print("r="+str(r))
        print("row="+str(self.row))
        if r > 0:
            self.app.root.after(int(constants.INTERVAL), lambda: self.animate_move(direction, d=d, r=r-1, original_row = original_row, original_column = original_column))
        else:
            self.update_pos(delta, original_row, original_column)

    def on_clock_tick(self, tick):
        improve_health = True
        state = self.state
        for stat in state:
            if stat != "health" and state[stat]["ticks"]:
                if not self.resting:
                    state[stat]["qty"]+=state[stat]["tick"]
                elif stat == "energy":
                    state[stat]["qty"]+=self.rest_fill_per_tick
                else:
                    # print(stat)
                    state[stat]["qty"]+=state[stat]["tick"]*self.resting_metabolic_rate

                stat_green = state[stat]["qty"] >= state[stat]["max"]/2
                improve_health = improve_health and stat_green
                state[stat]["qty"] = min(state[stat]["qty"], state[stat]["max"])
        if improve_health:
            state["health"]["qty"] += state["health"]["tick"]
            state["health"]["qty"] = min(state["health"]["qty"],state["health"]["max"])
        
        if state["energy"]["qty"] == state["energy"]["max"] and self.resting:
            self.wake()

        for monster in self.app.screen.monsters:
            d = maps.sprite_distance(self, monster)
            if d <= self.wake_distance and self.resting:
                self.wake()
        if self.resting:
            # print("changing frame")
            self.update_snore_sprite()
        self.app.update_status()
