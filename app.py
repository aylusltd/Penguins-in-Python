#!/usr/local/bin/python
from Tkinter import *
from PIL import Image, ImageTk
import constants
import sprites
import string
from keyhandlers import on_keypress
import craft
from starting_inventory import starting_inventory
import maps

MAKE_MONSTERS = True
MAKE_FISH = True
# MAKE_MONSTERS = False

class Application(Frame):
    g=constants.grid_size
    selected_square=None
    spears = []
    def save(self):
        maps.save(app=self)
        pass
    def load(self):
        maps.load(app=self)
        pass

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
        row = int(event.y/constants.grid_size)
        column = int(event.x/constants.grid_size)
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
        g = constants.grid_size
        # c=0
        for fish in self.screen.fishes:
            fish.moved = False
            fish.move(app=self)

        for monster in self.screen.monsters:
            # c+=1
            # print "Moving monster "+ str(c)
            not_moved = True
            d_y = monster.row - self.tux.row
            d_x = monster.column - self.tux.column
            grid = self.screen.grid
            if abs(d_x) < abs(d_y):
                if d_y < 0:
                    if grid[monster.row+1][monster.column].passable:
                        if not grid[monster.row+1][monster.column].occupied:
                            grid[monster.row][monster.column].occupied = False                        
                            self.screen.canvas.move(monster.sprite,0,g)
                            monster.row+=1
                            grid[monster.row][monster.column].occupied = True
                            not_moved=False
                        elif ( self.tux.row == monster.row+1 and 
                               self.tux.column == monster.column):
                            not_moved=False
                            self.tux.hit(1)
                        else:
                            # print "failure"
                            pass

                elif d_y > 0:
                    if grid[monster.row-1][monster.column].passable:
                        if not grid[monster.row-1][monster.column].occupied:
                            grid[monster.row][monster.column].occupied = False
                            self.screen.canvas.move(monster.sprite,0,-g)
                            monster.row-=1
                            grid[monster.row][monster.column].occupied = True
                            not_moved=False
                        elif ( self.tux.row == monster.row-1 and 
                               self.tux.column == monster.column):
                            not_moved=False
                            self.tux.hit(1)
                        else:
                            # print "failure"
                            pass
            if not_moved:
                if d_x < 0:
                    if grid[monster.row][monster.column+1].passable:
                        if not grid[monster.row][monster.column+1].occupied:
                            grid[monster.row][monster.column].occupied = False
                            self.screen.canvas.move(monster.sprite,g,0)
                            monster.column+=1
                            grid[monster.row][monster.column].occupied = True
                            not_moved=False
                        elif ( self.tux.row == monster.row and 
                            self.tux.column == monster.column + 1):
                            self.tux.hit(1)
                            not_moved=False
                        else:
                            print "failure"
                elif d_x > 0:
                    if grid[monster.row][monster.column-1].passable:
                        if not grid[monster.row][monster.column-1].occupied:
                            grid[monster.row][monster.column].occupied = False
                            self.screen.canvas.move(monster.sprite,-g,0)
                            monster.column-=1
                            grid[monster.row][monster.column].occupied = True
                            not_moved=False
                        elif ( self.tux.row == monster.row and 
                            self.tux.column == monster.column - 1):
                            self.tux.hit(1)
                            not_moved=False
                        else:
                            print "failure"
        self.root.after(constants.INTERVAL * 25, self.monsters_move)

    def addSprites(self):
        global MAKE_MONSTERS
        self.tux = sprites.Sprite(self)
        self.screen.monsters=[]
        self.screen.fishes=[]
        m = self.screen.monsters
        f = self.screen.fishes
        if MAKE_MONSTERS:
            for i in range(0,10):
                monster = sprites.Monster(self)
                if monster.placed: 
                    m.append(monster)
                    l = len(m) - 1
                    m[l].ind = l
        if MAKE_FISH:
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
            print "Dieded"

    def createWidgets(self):
        global root
        self.frame = Frame(root)
        self.frame2 = Frame(root)
        self.frame.pack(fill=BOTH, expand=1, side="left")

        self.screen = sprites.Screen(self)
        self.addSprites()
        self.screen.canvas.pack(fill=BOTH, expand=1)
        self.display_inventory()
        self.frame2.pack(fill=BOTH, expand=1, side="right")

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
        self.master=master
        self.counter=0
        self.root = root
        self.sprites = {}
        self.action=None

        self.craft = craft.Craft(app=self)

        Frame.__init__(self, master)
        # self.keypress = on_keypress
        self.pack()
        self.createWidgets()
        self.create_popups()
        self.root.after(constants.INTERVAL * 25, self.monsters_move)
        # master.after(1, lambda: master.focus_force())

        # self.animate()
        menubar = Menu(root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
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
    print "Couldn't destroy root. Maybe try a bigger drill?"