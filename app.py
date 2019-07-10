#!/usr/local/bin/python
import string
import tracemalloc

from PIL import Image, ImageTk
from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu

import craft
import sprites
import maps

import constants
from keyhandlers import on_keypress
from starting_inventory import starting_inventory

MALLOC_LOG = False
move_counter = 0
MALLOC_INTERVAL = 10

MAKE_MONSTERS = True
MAKE_FISH = True
# MAKE_MONSTERS = False
tracemalloc.start()
class Application(Frame):
    g=constants.grid_size
    selected_square=None
    spears = []
    def save(self):
        maps.save_world(app=self)

    def load(self):
        maps.load_world(app=self)

    def toggle_pause(self):
        self.pause = not self.pause

    def make_monster(self):
        s = self.selected_square
        x = s.column
        y = s.row
        m = self.screen.monsters
        monster = sprites.Monster(self, x=x, y=y)
        if monster.placed: 
            m.append(monster)
            l = len(m) - 1
            m[l].ind = l

    def make_fish(self):
        s = self.selected_square
        x = s.column
        y = s.row
        f = self.screen.fishes
        fish = sprites.Fish(self, x=x, y=y)
        if fish.placed: 
            f.append(fish)
            l = len(f) - 1
            f[l].ind = l

    def make_rocks(self):
        s = self.selected_square
        s.add_feature("rock", self)

    def make_trees(self):
        s = self.selected_square
        s.add_feature("tree", self)

    def make_water(self):
        s=self.selected_square
        s.passable=False
        s.square_type='water'
        self.screen.canvas.itemconfig(s.representation, fill='blue')
        self.selected_square=None

    def make_grass(self):
        s=self.selected_square
        s.passable=True
        s.square_type='grass'
        self.screen.canvas.itemconfig(s.representation, fill='green')
        self.selected_square=None

    def edit_square(self, event):
        grid_size = constants.grid_size
        row = int(event.y/grid_size)
        column = int(event.x/grid_size)
        # o = string.Template('Right Clicked {x:$column, y:$row}').substitute({'column':column, 'row': row})
        # print o
        ss = self.screen
        s = ss.grid[row][column]
        self.selected_square = s
        grass_only = ["Make Monster", "Make Trees", "Make Rocks", "Make Water"]
        water_only = ["Make Grass", "Make Fish"]
        # print s.square_type
        if s.square_type == 'grass':
            for g in grass_only:
                self.popup.entryconfig(g, state='normal')
            for w in water_only:
                self.popup.entryconfig(w, state='disabled')
        elif s.square_type == 'water':
            for g in grass_only:
                self.popup.entryconfig(g, state='disabled')
            for w in water_only:
                self.popup.entryconfig(w, state='normal')
        # print s.passable
        try:
            self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.popup.grab_release()

    def keypress(self, event):
        on_keypress(self, event)

    def monsters_move(self):
        global move_counter, MALLOC_INTERVAL, MALLOC_LOG
        if move_counter == MALLOC_INTERVAL and MALLOC_LOG:
            snapshot = tracemalloc.take_snapshot()
            constants.display_top(snapshot)
            move_counter = 0
        move_counter +=1
        # print(move_counter)
        
        g = constants.grid_size
        # c=0
        if not self.pause:
            for fish in self.screen.fishes:
                fish.moved = False
                fish.move(app=self)

            for monster in self.screen.monsters:
                monster.moved = False
                monster.move(app=self)
                
        self.root.after(constants.INTERVAL * 125, self.monsters_move)

    def add_sprites(self, tux_x=None, tux_y=None, monsters=[], fishes=[]):
        global MAKE_MONSTERS
        print('add_sprites')
        self.tux = sprites.Tux(self,x=tux_x, y=tux_y)
        
        if len(monsters)>0:
            print('value of monsters argument')
            print(monsters)
            raise Exception()
        self.screen.monsters=monsters
        self.screen.fishes=fishes
        m = self.screen.monsters
        f = self.screen.fishes
        print('self.screen.monsters')
        print(self.screen.monsters)
        print(fishes)
        if MAKE_MONSTERS and len(m) == 0:
            for i in range(0,1):
                monster = sprites.Monster(self)
                if monster.placed: 
                    m.append(monster)
                    l = len(m) - 1
                    m[l].ind = l
        if MAKE_FISH and len(f) == 0:
            for i in range(0,10):
                fish = sprites.Fish(self)
                if fish.placed: 
                    f.append(fish)
                    l = len(f) - 1
                    f[l].ind = l
        # Consumables added here
        sprites.Rocks(self)
        sprites.Trees(self)

    def display_inventory(self):
        self.inventory = starting_inventory
        self.update_inventory()

    def update_inventory(self):
        si=self.inventory
        row=1;
        for key in self.inventory:    
            si[key]["s"]=StringVar()
            si[key]["s"].set(self.inventory[key]["qty"])
            si[key]["l1"]=Label(self.frame2, text=si[key]["display"]+": ", bg="gray")
            si[key]["l2"]=Label(self.frame2, textvariable=si[key]["s"], bg="gray")
            si[key]["l1"].grid(row=row, column=0, sticky="we")
            si[key]["l2"].grid(row=row, column=1, sticky="we")
            row+=1
        if si["fish"]["qty"] <= 0:
            print("Dieded")

    def create_widgets(self):
        global root
        self.frame = Frame(root)
        self.frame2 = Frame(root)
        self.frame.pack(fill=BOTH, expand=1, side="left")

        self.screen = sprites.Screen(self)
        x=self.screen.current_map["x"]
        y=self.screen.current_map["y"]
        self.add_sprites()
        self.screen.grids[y][x] = maps.save(app=self, in_memory=True)
        self.screen.canvas.pack(fill=BOTH, expand=1)
        self.display_inventory()
        self.frame2.pack(fill=BOTH, expand=1, side="right")

        # Not used I think
        self.craft_button = Button(self.frame2, text="craft")
        self.craft_button.grid(row=0, column=0, sticky="we")
        self.craft_button["command"]=self.craft.create_window

        self.screen.canvas.focus_set()
        self.screen.canvas.bind("<Key>", self.keypress)

    def create_popups(self):
        self.popup = Menu(root, tearoff=0)
        self.popup.add_command(label="Make Grass", command=self.make_grass) # , command=next) etc...
        self.popup.add_command(label="Make Water", command=self.make_water)
        self.popup.add_separator()
        self.popup.add_command(label="Make Monster", command=self.make_monster)
        self.popup.add_command(label="Make Rocks", command=self.make_rocks)
        self.popup.add_command(label="Make Trees", command=self.make_trees)
        self.popup.add_command(label="Make Fish", command=self.make_fish)

    def __init__(self, master=None):
        self.pause=False
        self.starting_map = {}
        self.master=master
        self.counter=0
        self.root = root
        self.sprites = {}
        self.action=None

        self.craft = craft.Craft(app=self)

        Frame.__init__(self, master)
        # self.keypress = on_keypress
        self.pack()
        self.create_widgets()
        self.create_popups()
        self.root.after(constants.INTERVAL * 25, self.monsters_move)
        # master.after(1, lambda: master.focus_force())

        # self.animate()
        menubar = Menu(root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label="Open", command=self.load, accelerator="Cmd-L")
        filemenu.add_command(label="Save", command=self.save, accelerator="Cmd-S")
        filemenu.add_command(label="Pause", command=self.toggle_pause, accelerator="Cmd-P")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit, accelerator="Cmd-Q")
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)


root = Tk()
root.focus_force()
root.tkraise()
app = Application(master=root)
app.mainloop()
try: 
    root.destroy()
except:
    print("Couldn't destroy root. Maybe try a bigger drill?")