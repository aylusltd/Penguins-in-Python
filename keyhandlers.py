from imp import load_source
from os.path import dirname

import yaml

import constants, sprites, maps
listeners = []
from Classes.Dictate import Dictate
# mypath = dirname(__file__)
# Dictate = load_source('Dictate', mypath+'/Classes/Dictate.py').Dictate


with open("configs/keybindings.yaml", 'r') as stream:
    key_bindings = yaml.safe_load(stream)
props = ["key", "keycode", "keysym", "state"]
bound_keys={
    "None": {},
    "8": {},
    "9": {}
}

for state in bound_keys:
    for prop in props:
        bound_keys[state][prop] = {}

for action_class in key_bindings:
    for action in key_bindings[action_class]:
        for prop in props:
            try:
                temp = key_bindings[action_class][action][prop]
                if (
                    prop == "state" and 
                    temp is not None and 
                    (temp < 8 or temp > 9)
                    ):
                    raise Exception("Invalid state")
            except KeyError:
                # print(prop + " not set for key: " + action + ".")
                # print("Setting to None")
                key_bindings[action_class][action][prop]=None

for action_class in key_bindings:
    for action in key_bindings[action_class]:
        if key_bindings[action_class][action]["state"] is None:
            for prop in props:
                if prop != "state":
                    if key_bindings[action_class][action]["state"] == 8:
                        s = "8"
                    elif key_bindings[action_class][action]["state"] == 9:
                        s = "9"
                    else:
                        s = "None"
                    temp = key_bindings[action_class][action][prop]
                    bound_keys[s][prop][temp] = action_class + "_" + action

KEY_BINDINGS = Dictate(key_bindings)
# print(bound_keys)

def key_listener(key = None, keycode = None, keysym = None, state=None, key_obj=None):
    if key_obj is None:
        obj = {
            "key": key,
            "keycode": keycode,
            "keysym": keysym,
            "state": state
        }
        key_obj = Dictate(obj)

    def faux_wrapper(l):
        def wrapper(*args, **kwargs):
            
            # Have to learn how to write a reduce here
            all_None = True
            for key in key_obj:
                all_None = all_None and key_obj[key] is None
            if all_None:
                return None

            s = args[0]
            e = args[1]
            if ((key_obj.keycode is None or key_obj.keycode == e.keycode) and 
                (key_obj.key is None or key_obj.key == e.char) and
                (key_obj.keysym is None or key_obj.keysym==e.keysym)
                and key_obj.state is None and e.state!=8
                ):
                if s.pause:
                    return None
                else:
                    return l(*args, **kwargs)
            elif key_obj.state is not None:
                # print("state")
                # print(state)
                # print("e.state")
                # print(e.state)
                if state==e.state:
                    if ((key_obj.keycode is None or key_obj.keycode == e.keycode) and 
                        (key_obj.key is None or key_obj.key == e.char) and
                        (key_obj.keysym is None or key_obj.keysym==e.keysym)
                        ):
                        return l(*args, **kwargs)
            else:
                # print(e)
                return None
        listeners.append(wrapper)
        return wrapper
    return faux_wrapper

def spear_check(l):
    def wrapper(*args, **kwargs):
        s = args[0]
        e = args[1]
        if s.inventory["spear"]["qty"] <= 0:
            return None
        else:
            s.inventory["spear"]["qty"] -=1
            s.update_inventory()
            return l(s,e)
    return wrapper

def resting_check(l):
    def wrapper(*args, **kwargs):
        s = args[0]
        e = args[1]
        if s.tux.resting:
            return None
        else:
            return l(s,e)
    return wrapper

def move_tux(l):
    def wrapper(*args, **kwargs):
        s=args[0]
        grid = s.screen.grid
        grid[s.tux.row][s.tux.column].occupied = False
        grid[s.tux.row][s.tux.column].has_tux = False
        l(*args, **kwargs)
        grid[s.tux.row][s.tux.column].occupied = True
        grid[s.tux.row][s.tux.column].has_tux = True
    return wrapper

# CMD+s (So far only tested right CMD)
@key_listener(key="s", state=8)
def save_game(s,e):
    print("saving")
    maps.save_world(app=s)

# CMD+l
@key_listener(key="l", state=8)
def load_game(s,e):
    print("loading")
    maps.load_world(app=s)

# CMD+Shift+s
@key_listener(key="s", state=9)
def save_game(s,e):
    print("saving single map")
    maps.save(app=s)

# CMD+p
@key_listener(key="p", state=8)
def pause_game(s,e):
    print("toggling pause")
    s.pause = not s.pause

@key_listener(key_obj=KEY_BINDINGS.spear.left)
@spear_check
@resting_check
def spear_left(s,e):
    y = s.tux.row
    x = s.tux.column
    s = sprites.Spear(s, d=90, x=x, y=y)
    # print "spear_left"

@key_listener(key_obj=KEY_BINDINGS.spear.right)
@spear_check
@resting_check
def spear_right(s,e):
    # print "spear_right"
    y = s.tux.row
    x = s.tux.column
    s = sprites.Spear(s, d=270, x=x, y=y)
    # print "spear_right"

@key_listener(key_obj=KEY_BINDINGS.spear.up)
@spear_check
@resting_check
def spear_up(s,e):
    y = s.tux.row
    x = s.tux.column
    s = sprites.Spear(s, d=0, x=x, y=y)
    # print "spear_up"

@key_listener(key_obj=KEY_BINDINGS.spear.down)
@spear_check
@resting_check
def spear_down(s,e):
    y = s.tux.row
    x = s.tux.column
    s = sprites.Spear(s, d=180, x=x, y=y)
    # print "spear_down"

@key_listener(key="h")
@resting_check
def harvest(s,e):
    r = s.tux.row
    c = s.tux.column
    g = s.screen.grid
    if g[r][c].has_tree:
        s.inventory["wood"]["qty"]+=10
        g[r][c].has_tree=False
        s.screen.canvas.delete(g[r][c].sprites["tree_sprite"])
    elif g[r][c].has_rock:
        s.inventory["rock"]["qty"]+=10
        g[r][c].has_rock=False
        s.screen.canvas.delete(g[r][c].sprites["rock_sprite"])
    s.update_inventory()    
    # print "harvest"

@key_listener(key="r")
@resting_check
def craft_spear(s,e):
    key = "spear"
    ingredients = ["wood", "wood", "rock", "rock"]
    inventory = s.inventory
    if has_ingredients(ingredients, inventory):
        consume_ingredients(ingredients, inventory)
        inventory[key]["qty"]+=1
    s.update_inventory()    
    # print "craft spear"

@key_listener(key="b")
@resting_check
def craft_brick(s,e):
    key = "brick"
    ingredients = ["rock", "rock"]
    inventory = s.inventory
    if has_ingredients(ingredients, inventory):
        consume_ingredients(ingredients, inventory)
        inventory[key]["qty"]+=1
    s.update_inventory()    
    # print "craft brick"

@key_listener(key="l")
@resting_check
def craft_wall(s,e):
    key = "wall"
    ingredients = ["brick", "brick", "brick", "brick"]
    inventory = s.inventory
    if has_ingredients(ingredients, inventory):
        consume_ingredients(ingredients, inventory)
        inventory[key]["qty"]+=1
    s.update_inventory()    
    # print "craft wall"

@key_listener(key="q")
@resting_check
def place_fire(s,e):
    key = "fire"
    ingredients = ["wood", "wood", "rock", "rock"]
    inventory = s.inventory
    r = s.tux.row
    c = s.tux.column
    g = s.screen.grid
    square = g[r][c]
    if has_ingredients(ingredients, inventory):
        consume_ingredients(ingredients, inventory)
        sprites.Fire(app=s, x=c, y=r)
        s.update_inventory()
    # print "place wall"

@key_listener(key="p")
@resting_check
def place_wall(s,e):
    key = "wall"
    ingredients = ["wall"]
    inventory = s.inventory
    r = s.tux.row
    c = s.tux.column
    g = s.screen.grid
    square = g[r][c]
    if has_ingredients(ingredients, inventory):
        consume_ingredients(ingredients, inventory)
        square.add_feature(feature="wall", app=s, passable=False)
        s.update_inventory()
    # print "place wall"

@key_listener(key="z")
@resting_check
def destroy_wall(s,e):
    key = "wall"
    # ingredients = ["wall"]
    # inventory = s.inventory
    screen = s.screen
    r = s.tux.row
    c = s.tux.column
    g = s.screen.grid
    square = g[r][c]
    touching_wall = screen.neighbor_has(feature=key, i=r, j=c)
    if touching_wall:
        s.action = "destroy wall"
    # print "destroying wall"

@key_listener(key="o")
@resting_check
def rest(s,e):
    s.tux.rest()

@key_listener(key="e")
@resting_check
def eat_fish(s,e):
    ingredients = ["fish"]
    inventory = s.inventory
    consume_ingredients(ingredients, inventory)
    s.tux.increment_stat(stat="hunger", qty=10)
    s.update_status()
    s.update_inventory()

@key_listener(key=" ")
@resting_check
def drink_water(s,e):
    print("drink water")
    screen = s.screen
    r = s.tux.row
    c = s.tux.column
    g = screen.grid
    square = g[r][c]
    touching_water = screen.neighbor_type(square_type="water", i=r, j=c)
    if touching_water:
        s.tux.increment_stat(stat="thirst", qty=10)
        s.update_status()
    else:
        print("not touching water")

@key_listener(key="f")
@resting_check
def catch_fish(s,e):
    key = "fish"
    # ingredients = ["fish"]
    # inventory = s.inventory
    # s.config(cursor='circle red red')
    screen = s.screen
    r = s.tux.row
    c = s.tux.column
    g = s.screen.grid
    square = g[r][c]
    touching_fish = screen.neighbor_has(feature=key, i=r, j=c)
    if touching_fish:
        s.action = "catch fish"
    # print "destroying wall"

def has_ingredients(ingredients, inventory):
    t={}
    for i in inventory:
        t[i]=inventory[i]["qty"]
    for ingredient in ingredients:
        if t[ingredient] < 1:
            return False
        t[ingredient]-=1
    return True

def consume_ingredients(ingredients, inventory):
    for ingredient in ingredients:
        inventory[ingredient]["qty"]-=1


# @key_listener(keycode=8320768)
@key_listener(key_obj=KEY_BINDINGS.move.up)
@move_tux
def move_up(s,e):
    g=s.g
    h=len(s.screen.grid)
    w=len(s.screen.grid[0])
    if s.tux.row > 0:
            if s.screen.grid[s.tux.row-1][s.tux.column].passable:
                s.screen.canvas.move(s.tux.sprite,0,-g)
                s.tux.row-=1
    else:
        s.screen.make_next_screen(direction="Up", tux_x=s.tux.column, tux_y=h-1)

# @key_listener(keycode=8255233)
@key_listener(key_obj=KEY_BINDINGS.move.down)
@move_tux
def move_down(s,e):
    g=s.g
    if s.tux.row < s.max_row:
        if s.screen.grid[s.tux.row+1][s.tux.column].passable:
            s.screen.canvas.move(s.tux.sprite,0,g)
            s.tux.row+=1
    else:
        s.screen.make_next_screen(direction="Down", tux_x=s.tux.column, tux_y=0)

# @key_listener(keycode=8124162)
@key_listener(key_obj=KEY_BINDINGS.move.left)
@move_tux
def move_left(s,e):
    g=s.g
    if s.tux.column > 0:
        if s.screen.grid[s.tux.row][s.tux.column-1].passable:
            s.screen.canvas.move(s.tux.sprite,-g,0)
            s.tux.column-=1
    else:
        s.screen.make_next_screen(direction="Left", tux_x=s.max_column, tux_y=s.tux.row)

# @key_listener(keycode=8189699)
@key_listener(key_obj=KEY_BINDINGS.move.right)
@move_tux
def move_right(s,e):
    g=s.g
    if s.tux.column < s.max_column:
        if s.screen.grid[s.tux.row][s.tux.column+1].passable:
            s.screen.canvas.move(s.tux.sprite,g,0)
            s.tux.column+=1
    else:
        s.screen.make_next_screen(direction="Right", tux_x=0, tux_y=s.tux.row)

def on_keypress(s, event):
    h = constants.bounds["y"][1]
    w = constants.bounds["x"][1]
    g = constants.grid_size
    c = s.screen.canvas
    p=c.coords(s.tux.sprite)

    current_row = int((p[1]-4)/g)
    current_column = int((p[0]-4)/g)
    s.tux.row=current_row
    s.tux.column=current_column
    s.max_row = int(h/g)-1
    s.max_column = int(w/g)-1
    s.screen.grid[current_row][current_column].occupied = False
    
    for l in listeners:
            l(s,event)
    s.screen.grid[s.tux.row][s.tux.column].occupied = True
    # s.root.after(constants.INTERVAL*2, s.monsters_move)