import json
import math

from tkinter import filedialog

import constants
import sprites

def save_world(app, filename=None, in_memory=False):
    prev_state = app.pause
    app.pause=True
    if filename is None and in_memory is False:
        filename=filedialog.asksaveasfilename(initialdir = "~/Desktop",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    if '.json' in filename:
        print("filename")
        print(filename)
        x=app.screen.current_map["x"]
        y=app.screen.current_map["y"]
        app.screen.grids[y][x] = save(app=app, in_memory=True)

        f=app.screen.grids
        my_map = {}
        my_map["grids"] = f
        my_map["current_screen"] = app.screen.current_map
        # my_map["current_inventory"] = app.inventory
        inventory = {}
        for key in app.inventory:
            inventory[key] = {}
            inventory[key]["display"] = app.inventory[key]["display"]
            inventory[key]["qty"] =app.inventory[key]["qty"]
        my_map["current_inventory"] = inventory
        print(app.screen.current_map)

        with open(filename, 'w') as myfile:
                j = json.dumps(my_map)
                myfile.write(j)
                myfile.close()
    app.pause=prev_state

def load_world(app, filename=None, from_memory=None):
    prev_state = app.pause
    app.pause=True
    if filename is None and from_memory is None:
        filename=filedialog.askopenfilename(initialdir = "~/Desktop",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    if '.json' in filename:
        with open(filename, 'rb') as myfile:
            r = myfile.read()
            myfile.close()
            r = json.loads(r)
        app.screen.grids = r["grids"]
        app.screen.current_map=r["current_screen"]
        # print(app.screen.current_map)

        y=app.screen.current_map["y"]
        x=app.screen.current_map["x"]

        g=app.screen.grids[y][x]
        
        app.inventory = my_map["current_inventory"]
        load(app, from_memory=g)
    app.pause=prev_state

def load(app, filename=None, from_memory=None):
    if filename is None and from_memory is None:
        filename=filedialog.askopenfilename(initialdir = "~/Desktop",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    if from_memory is None and '.json' in filename:
        with open(filename, 'rb') as myfile:
            r = myfile.read()
            myfile.close()
        r = json.loads(r)
    elif from_memory is not None:
        r=from_memory
    else: 
        return
    grid = r["grid"]
    saved_sprites = r["sprites"]
    tux = r["tux"]
    screen_rows = []
    i=0
    canvas = app.screen.canvas
    canvas.delete("all")
    for file_row in grid:
        screen_rows.append([])
        for cell in file_row:
            # def __init__(self, row, column, canvas, app, g=constants.grid_size, square_type='grass')
            s = sprites.Square(
                    row         = int(cell["row"]), 
                    column      = int(cell["column"]),
                    app         = app,
                    canvas      = canvas,
                    square_type = cell["square_type"]
                )
            
            # def add_feature(self, feature, app, required_type="grass"):
            if cell["has_tree"] == "True":
                s.add_feature(feature = "tree", app = app)
            if cell["has_rock"] == "True":
                s.add_feature("rock", app = app) 
            screen_rows[i].append(s)
        i+=1
    app.screen.grid = screen_rows
    app.tux = sprites.Tux(
            app, 
            x=tux["column"],
            y=tux["row"]
        )
    app.screen.monsters=[]
    app.screen.fishes = []
    m = app.screen.monsters
    f = app.screen.fishes
    for sprite in saved_sprites:
        # def __init__(self, app, x=None, y=None)
        x = sprite["column"]
        y = sprite["row"]
        if sprite["type"] == "virus":
            m.append(sprites.Monster(
                app = app, 
                x = x,
                y = y
            ))
            l = len(m) - 1
            m[l].ind = l
            app.screen.grid[y][x].occupied=True
        elif sprite["type"] == "fish":
            f.append(sprites.Fish(
                app = app, 
                x = x,
                y = y
            ))
            l=len(f)-1
            f[l].ind = l


def save(app, filename=None, in_memory=False):
    if filename is None and in_memory is False:
        filename=filedialog.asksaveasfilename(initialdir = "~/Desktop",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    file_rows=[]
    i=0
    for screen_row in app.screen.grid:
        file_rows.append([])
        for cell in screen_row:
            obj={}
            obj["passable"]    = str(cell.passable)
            obj["square_type"] = str(cell.square_type)
            obj["row"]         = str(cell.row)
            obj["column"]      = str(cell.column)
            obj["occupied"]    = str(cell.occupied)
            obj["has_tree"]    = str(cell.has_tree)
            obj["has_rock"]    = str(cell.has_rock)
            obj["has_tux"]     = str(cell.has_tux)
            obj["sprites"]     = str(cell.sprites)
            file_rows[i].append(obj)
        i+=1
    sprites_to_write = []
    for monster in app.screen.monsters:
        m={}
        m["row"] = monster.row
        m["column"] = monster.column
        m["type"] = monster.type
        sprites_to_write.append(m)
    for fish in app.screen.fishes:
        f={}
        f["row"] = fish.row
        f["column"] = fish.column
        f["type"] = "fish"
        sprites_to_write.append(f)
    tux = {}
    tux["row"] = app.tux.row
    tux["column"] = app.tux.column
    tux["type"] = "tux"
    # sprites.append(tux)
    # print(file_rows)
    # print(sprites)
    f={}
    f["grid"] = file_rows
    f["sprites"] = sprites_to_write
    f["tux"] = tux
    print(f["tux"])
    if in_memory is False:
        with open(filename, 'w') as myfile:
            j = json.dumps(f)
            myfile.write(j)
            myfile.close()
    else:
        return f

def sprite_distance(sprite_a, sprite_b):
    x1 = sprite_a.column
    x2 = sprite_b.column
    y1 = sprite_a.row
    y2 = sprite_b.row
    
    return euclid(x1,y1,x2,y2)

def euclid(x1, y1, x2, y2):
    d_x = abs(x1-x2)
    d_y = abs(y1-y2)

    d = math.sqrt((d_x**2) + (d_y**2))
    return d

# Returns a constants.Direction or None
# None signifies same square
def direction_to_target(source, target):
    x1 = source.column
    x2 = target.column
    y1 = source.row
    y2 = target.row

    d_x = x1-x2
    d_y = y1-y2

    directions=[]
    # if closer largest gap first
    if abs(d_x) >= abs(d_y):
        if d_x < 0:
            directions.append(constants.EAST)
        elif d_x > 0:
            directions.append(constants.WEST)
        if d_y > 0:
            directions.append(constants.NORTH)
        elif d_y < 0:
            directions.append(constants.SOUTH)
    elif abs(d_x) < abs(d_y):
        if d_y > 0:
            directions.append(constants.NORTH)
        elif d_y < 0:
            directions.append(constants.SOUTH)
        if d_x < 0:
            directions.append(constants.EAST)
        elif d_x > 0:
            directions.append(constants.WEST)

    return directions

def move(direction, distance):
    delta = {
        "x" : 0,
        "y" : 0
    }
    distance = int(distance)
    if direction == constants.EAST:
        delta["x"] += distance
    elif direction == constants.WEST:
        delta["x"] -= distance
    elif direction == constants.NORTH:
        delta["y"] -= distance
    elif direction == constants.SOUTH:
        delta["y"] += distance
    else:
        raise Exception("Invalid Direction")

    return delta


