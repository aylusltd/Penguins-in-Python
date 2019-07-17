#!/usr/local/bin/python
import os
import string
import tracemalloc

from threading import Thread

from PIL import Image, ImageTk
from tkinter import Tk, Frame, BOTH, StringVar, Label, Button, Menu, Canvas, ttk, Toplevel
import pyglet

import craft
import sprites as Sprites
import maps
import constants

from keyhandlers import on_keypress
from starting_inventory import starting_inventory
from Classes.Sound import Sound

MALLOC_LOG = False
move_counter = 0
MALLOC_INTERVAL = 10

MAKE_MONSTERS = True
MAKE_FISH = True
# MAKE_MONSTERS = False

tracemalloc.start()
class DragToplevel(Toplevel):
    def __init__(self, master, image, x, y):
        Toplevel.__init__(self, master)
        self.overrideredirect(True)
        self.geometry('+%i+%i' % (x, y))
        self.image = image
        self.label = Label(self, image=image, bg='red')
        self.label.pack()

    def move(self, x, y):
        self.geometry('+%i+%i' % (x, y))

    def end(self):
        self.label.destroy()
        self.destroy()

class Canvas_Drag_Manager(Toplevel):
    dragging=False
    source=None
    root = None

    def on_start(self, event):
        if self.dragging:
            return None
        x,y = event.widget.winfo_pointerxy()
        self.source = target = event.widget.winfo_containing(x,y)
        items = target.find_closest(event.x, event.y)
        if items:
            self.image = target.itemcget(items[0], 'image')
            for hook in self.drag_hooks:
                t = hook(event, target, self.image)
                if t is False:
                    return None
        self.TL = DragToplevel(self.root, self.image, x, y)
        self.dragging = True

    def on_drag(self, event):
        if self.dragging is False:
            return None
        x,y = event.widget.winfo_pointerxy()
        # self.target = event.widget.winfo_containing(x,y)
        for hook in self.move_hooks:
            hook(event, self.source, self.image)
        self.TL.move(x,y)

    def on_drop(self, event):
        # find the widget under the cursor
        if self.dragging is False:
            return None
        x,y = event.widget.winfo_pointerxy()
        self.drop_target = event.widget.winfo_containing(x,y)
        for hook in self.drop_hooks:
            hook(event, self.drop_target, self.source, self.image)
        self.TL.end()
        del(self.image)
        del(self.source)
        self.dragging=False

    def add_drag_hook(self, hook):
        self.drag_hooks.append(hook)
        return len(self.drag_hooks)-1

    def remove_drag_hook(self, index):
        del self.drag_hooks[index]

    def add_drop_hook(self, hook):
        self.drop_hooks.append(hook)
        return len(self.drop_hooks)-1

    def remove_drop_hook(self, index):
        del self.drop_hooks[index]

    def add_move_hook(self, hook):
        self.move_hooks.append(hook)
        return len(self.move_hooks)-1

    def remove_move_hook(self, index):
        del self.move_hooks[index]

    def __init__(self, root, canvases, drop_hook=None, move_hook=None, drag_hook=None):
        # tkinter.Toplevel.__init__(self, master)
        if type(canvases) is list:
            self.canvases = canvases
        elif canvases is not None:
            self.canvases = [canvases]
        else:
            self.canvases=[]

        if type(drop_hook) is list:
            self.drop_hooks = drop_hook
        elif drop_hook is not None:
            self.drop_hooks = [drop_hook]
        else:
            self.drop_hooks=[]

        if type(move_hook) is list:
            self.move_hooks = move_hook
        elif move_hook is not None:
            self.move_hooks = [move_hook]
        else:
            self.move_hooks=[]

        if type(drag_hook) is list:
            self.drag_hooks = drag_hook
        elif drag_hook is not None:
            self.drag_hooks = [drag_hook]
        else:
            self.drag_hooks=[]

        self.root = root

        for widget in self.canvases:
            widget.bind("<ButtonPress-1>", self.on_start)
            widget.bind("<B1-Motion>", self.on_drag)
            widget.bind("<ButtonRelease-1>", self.on_drop)
            widget.configure(cursor="hand1")

class Application(Frame):
    Canvas_Drag_Manager=Canvas_Drag_Manager
    g=constants.grid_size
    selected_square=None
    tick=0
    spears = []
    sprites = []
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
        monster = Sprites.Monster(self, x=x, y=y)
        if monster.placed: 
            m.append(monster)
            self.sprites.append(monster)
            l = len(m) - 1
            m[l].ind = l

    def make_fish(self):
        s = self.selected_square
        x = s.column
        y = s.row
        f = self.screen.fishes
        fish = Sprites.Fish(self, x=x, y=y)
        if fish.placed: 
            f.append(fish)
            self.sprites.append(fish)
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
            for sprite in self.sprites:
                # sprite.on_tick(self.tick)
                sprite.on_clock_tick(self.tick)
                try:
                    sprite.on_clock_tick(self.tick)
                except AttributeError as err:
                    print(sprite)
                    raise err

            self.tux.on_clock_tick(self.tick)
            self.tick+=1
        self.root.after(constants.INTERVAL * 25, self.monsters_move)

    def add_sprites(self, tux_x=None, tux_y=None, monsters=[], fishes=[]):
        global MAKE_MONSTERS
        print('add_sprites')
        self.tux = Sprites.Tux(self,x=tux_x, y=tux_y)
        
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
                monster = Sprites.Monster(self)
                if monster.placed: 
                    m.append(monster)
                    self.sprites.append(monster)
                    l = len(m) - 1
                    m[l].ind = l
        if MAKE_FISH and len(f) == 0:
            for i in range(0,10):
                fish = Sprites.Fish(self)
                if fish.placed: 
                    f.append(fish)
                    self.sprites.append(fish)
                    l = len(f) - 1
                    f[l].ind = l
        # Consumables added here
        Sprites.Rocks(self)
        Sprites.Trees(self)

    def display_inventory(self):
        self.inventory = starting_inventory
        self.update_inventory()

    def display_status(self, height=constants.bounds["y"][1]/4, width=constants.bounds["x"][1], grid=constants.grid_size):
        g=grid
        h=g * 1.5
        w=width
        self.status_canvas=Canvas(self.frame3, height=h+10, width=w+10, background="gray")
        self.update_status()

    def update_inventory(self):
        si=self.inventory
        # 1000 x 180
        # g = 40
        row=1;
        for key in self.inventory:
            if self.inventory[key]["qty"] > 0:    
                si[key]["s"]=StringVar()
                si[key]["s"].set(self.inventory[key]["qty"])
                si[key]["l1"]=Label(self.frame2, text=si[key]["display"]+": ", bg="gray")
                si[key]["l2"]=Label(self.frame2, textvariable=si[key]["s"], bg="gray")
                si[key]["l1"].grid(row=row, column=0, sticky="we")
                si[key]["l2"].grid(row=row, column=1, sticky="we")
                row+=1
            else:
                try: 
                    si[key]["s"]
                    si[key]["l1"].destroy()
                    si[key]["l2"].destroy()
                    si[key]["s"]= None
                except KeyError:
                    pass

    def update_status(self):
        g = self.g
        state = self.tux.state
        canvas = self.status_canvas
        row = 0.25
        column = 0
        span = 3

        # Stats can be dynamically added
        state["mana"] = {
              "display": "Mana",
              "qty" : 100,
              "full": "blue",
              "empty": "red",
              "tick": 1,
              "max": 100,
              "ticks": False,
              "label" : "white"
        }

        for stat in state:
            q = state[stat]["qty"]
            m = state[stat]["max"]
            try:
                canvas.delete(state[stat]["background_rect"])
                canvas.delete(state[stat]["foreground_rect"])
                canvas.delete(state[stat]["l1"])
            except KeyError:
                pass

            state[stat]["background_rect"] = canvas.create_rectangle(
                (column*g)+5, 
                (row*g)+5, 
                ((column+span)*g)+5, 
                ((row+1)*g)+5,
                fill=state[stat]["empty"],
                outline="")
            state[stat]["foreground_rect"] = canvas.create_rectangle(
                (column*g)+5, 
                (row*g)+5, 
                (((column+(span*q/m))*g)+5), 
                ((row+1)*g)+5,
                fill=state[stat]["full"],
                outline="")
            # state[stat]["s"] = StringVar()
            state[stat]["s"]= state[stat]["display"]+": " + str(int(q))

            state[stat]["l1"] = canvas.create_text(((column+1)*g+10, row*g+10), text=state[stat]["s"], fill=state[stat]["label"])
            # state[stat]["l1"]=Label(self.frame3, text=state[stat]["display"]+": ", bg="gray")
            # state[stat]["l2"]=Label(self.frame3, textvariable=state[stat]["s"], bg="gray")
            # state[stat]["l1"].grid(row=0, column=column*2, sticky="we")
            # state[stat]["l2"].grid(row=0, column=column*2+1, sticky="we")
            column+=span + 1

    def create_widgets(self):
        global root
        self.frame = Frame(root)
        self.frame2 = Frame(root)
        self.frame3 = Frame(root)

        self.screen = Sprites.Screen(self)
        x=self.screen.current_map["x"]
        y=self.screen.current_map["y"]

        self.add_sprites()
        self.screen.grids[y][x] = maps.save(app=self, in_memory=True)
        self.screen.canvas.pack(fill=BOTH, expand=1)
        self.display_inventory()
        self.display_status()

        self.frame3.pack(fill="x", side="bottom")
        self.status_canvas.pack(fill=BOTH, expand=1)

        # Switched to ttk button for Mac. Need to test on other systems
        self.craft_button = ttk.Button(self.frame2, text="Craft")
        self.craft_button.grid(row=0, column=0, columnspan=2, sticky="we")
        self.craft_button["command"]=self.craft.create_window
        self.frame2.pack(fill=BOTH, expand=1, side="right")
        
        self.frame.pack(fill=BOTH, expand=1, side="left")
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

    def bg_music_player(self):
        snd = Sound('sounds/TuxBackground.wav')
        snd.load()
        snd.play()
        # snd = pyglet.media.load('sounds/TuxBackground.wav')
        # player = pyglet.media.Player()
        # player.queue(snd)
        # player.loop = True
        # player.eos_action = player.EOS_LOOP
        # player.play()

    def __init__(self, master=None):
        self.pause=False
        self.starting_map = {}
        self.master=master
        self.counter=0
        self.root = root
        self.sprite_images = {}
        self.action=None
        self.g = constants.grid_size

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
        # Delet later, debugging craft menu
        # self.craft.create_window()
        self.bg_music_player()

root = Tk()
root.focus_force()
root.tkraise()
app = Application(master=root)

def main():
    app.mainloop()
    # pyglet.app.run()    
    try: 
        root.destroy()
    except:
        print("Couldn't destroy root. Maybe try a bigger drill?")

if __name__ == '__main__':
    main()