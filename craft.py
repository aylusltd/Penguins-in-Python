import copy

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import yaml

import constants

class Table_square(constants.correction):
    image = None
    ingredient = None
    inventory_square = None
    def __init__(self, x, y, crafting_canvas, inventory_canvas, app):
        fill="gray"
        g = constants.grid_size
        self.rect = crafting_canvas.create_rectangle(
                (y*g)+5, 
                (x*g)+5, 
                ((y+1)*g)+5, 
                ((x+1)*g)+5,
                fill=fill)
        self.row = y
        self.column=x
        self.crafting_canvas = crafting_canvas
        self.inventory_canvas = inventory_canvas
        self.app = app

    def add_ingredient(self, inventory_square):
        if inventory_square is None:
            return False
        self.inventory_square = inventory_square
        ingredient = inventory_square.item
        self.ingredient = ingredient
        si = self.app.inventory
        column = self.column
        row = self.row
        g = constants.grid_size
        img = Image.open("sprites/" + si[ingredient]["img"])
        img.thumbnail((g,g))
        self.my_image = ImageTk.PhotoImage(img)
        self.image_index=self.crafting_canvas.create_image(((column+0.5)*g)+5, ((row+0.5)*g)+5, image=self.my_image)
        si[ingredient]["qty"]-=1
        self.inventory_canvas.delete(self.inventory_square.text)
        self.inventory_square.text=self.inventory_canvas.create_text(((self.inventory_square.column+1)*g*1.2+10, (self.inventory_square.row+0.75)*g*1.2+10), text=si[ingredient]["qty"])

    def remove_ingredient(self, increment_inventory=True):
        if self.ingredient is None:
            return False

        column = self.column
        row = self.row
        g = constants.grid_size
        ingredient=self.ingredient
        si = self.app.inventory
        self.crafting_canvas.delete(self.image_index)
        self.image_index=None
        if increment_inventory:
            si[ingredient]["qty"]+=1

        self.inventory_canvas.delete(self.inventory_square.text)
        self.inventory_square.text=self.inventory_canvas.create_text(((self.inventory_square.column+1)*g*1.2+10, (self.inventory_square.row+0.75)*g*1.2+10), text=si[ingredient]["qty"])
        self.ingredient = None
        
        return True


class Inventory_Square(constants.correction):
    def __init__(self, x, y, canvas, app, item, image=None, text=None, icon=None):
        self.inventory = app.inventory
        fill="gray"
        g = constants.grid_size * 1.2

        self.row = y
        self.column=x
        self.canvas = canvas
        self.app = app
        self.item = item
        self.qty = self.inventory[item]["qty"]
        si = self.inventory
        row = y
        column = x
        
        self.text=si[item]["qty"]
        self.text=canvas.create_text(((column+1)*g+10, (row+0.75)*g+10), text=self.text)
        img = Image.open("sprites/" + si[item]["img"])
        img.thumbnail((g,g))
        self.image = si[item]["image"] = ImageTk.PhotoImage(img)
        self.icon = si[item]["icon"]=canvas.create_image(((column+0.5)*g)+5, ((row+0.5)*g)+5, image=si[item]["image"])


class Craft(constants.correction):
    def load_recipes(self):
        # read recipes from yaml
        with open("configs/recipes.yaml", 'r') as stream:
            recipes = yaml.safe_load(stream)
        # for each
        for r in recipes:
            # make table
            # pad table to 10 x 10
            recipe = recipes[r]
            for i in range(0,10):
                try:
                    recipe[i]
                except IndexError:
                    recipe.append([])
                for j in range(0,10):
                    try:
                        recipe[i][j]
                    except IndexError:
                        recipe[i].append('0')
            # flatten
            recipe = sum(recipe, [])
            # convert to string
            recipe=''.join(recipe)
            # trim leading and trailing 0's
            recipe=recipe.strip('0')
            recipes[r] = recipe
        self.recipes=recipes

    def check_recipe(self):
        g = constants.grid_size
        recipe=self.craft_grid
        inventory = self.app.inventory
        arr = []
        consumed_table_squares=[]
        # pad to 10 x 10
        for i in range(0,10):
            arr.append([])
            for j in range(0,10):
                try:
                    arr[i].append(recipe[i][j].ingredient)
                    if arr[i][j] == None:
                        arr[i][j] = '0'
                    else:
                        consumed_table_squares.append(recipe[i][j])
                except IndexError:
                    arr[i].append('0')
        
        # flatten
        recipe = sum(arr, [])
        # convert to string
        recipe=''.join(recipe)
        # trim leading and trailing 0's
        my_recipe=recipe.strip('0')
        item_to_make=None
        recipes = self.recipes
        for recipe in recipes:        
            # check to see if string contains recipe
            their_recipe = recipes[recipe]
            if their_recipe in my_recipe:
                # check to see if any other ingredients
                if len(their_recipe) == len(my_recipe) and their_recipe.count('0') == my_recipe.count('0'):
                    item_to_make = recipe
            
        # if no recipe matched alert user
        if item_to_make is None:
            # alert user
            pass
        else:
            # Add new to inventory
            try:
                inventory[item_to_make]
            except KeyError:
                inventory[item_to_make] = {}

            print("made 1 " + item_to_make)
            inventory[item_to_make]["qty"]+=1
            sq = self.inventory_dict[item_to_make]
            self.inventory_canvas.delete(sq.text)
            sq.text =self.inventory_canvas.create_text(((sq.column+1)*g*1.2+10, (sq.row+0.75)*g*1.2+10), text=inventory[item_to_make]["qty"])
            # remove sprites from table
            for square in consumed_table_squares:
                square.remove_ingredient(increment_inventory=False)
            self.app.update_inventory()

    def render_surface(self):
        # self.canvas.delete("all")
        height=self.table_size[1]
        width =self.table_size[0]
        column=0
        row =0
        self.craft_grid=[]
        
        # g = self.craft_grid
        for i in range(0,height):
            column=0
            self.craft_grid.append([])
            # print app.grid[i]
            for j in range(0,width):
                s = Table_square(
                    x=column,
                    y=row,
                    crafting_canvas=self.canvas,
                    inventory_canvas=self.inventory_canvas,
                    app=self.app
                    )
                self.craft_grid[i].append(s)
                column+=1
            row+=1
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def render_inventory(self):
        self.inventory_canvas.delete("all")
        app = self.app
        frame = self.frame2
        g = constants.grid_size
        g*=1.2
        canvas = self.inventory_canvas
        si = self.inventory
        row=0;
        column=0
        self.inventory_grid = []
        self.inventory_dict = {}
        for item in si:
            self.inventory_grid.append([])
            item_square = Inventory_Square(
                x=column,
                y=row,
                canvas=self.inventory_canvas,
                app=self.app,
                item = item
                )
            self.inventory_grid[row].append(item_square)
            self.inventory_dict[item]=item_square                      
            row+=1
            if row > self.MAX_ROWS:
                column+=1
                row=0
        self.inventory_canvas.pack(fill=tk.BOTH, expand=1)

    def craft_drop_hook(self, event, drop_target, source, image):
        # find target square
        x = event.x
        y = event.y
        g = constants.grid_size
        try:
            target_square = self.craft_grid[int(y/g)][int(x/g)]

            if target_square.ingredient:
                target_square.remove_ingredient()
            target_square.add_ingredient(self.ingredient)
            self.ingredient = None
        except IndexError:
            pass
        

    def craft_drag_hook(self, event, source, image):
        # set active ingredient
        x = event.x
        y = event.y
        g = constants.grid_size * 1.2
        source_square = None
        try:
            source_square = self.inventory_grid[int(y/g)][int(x/g)]
        except IndexError:
            pass
        if source_square is not None:
            # print("From Inventory")
            self.ingredient = source_square
            item = source_square.item
            si = self.app.inventory
            if self.app.inventory[item]["qty"] > 0:
                return True
            else:
                return False
        else:
            try:
                source_square = self.craft_grid[int(y/g)][int(x/g)]
            except IndexError:
                pass
    
            if source_square is not None:
                # print("From Table")
                if source_square.inventory_square is None:
                    return False
                else:
                    self.ingredient = source_square.inventory_square
                    source_square.remove_ingredient()
                return True

        return False

    def create_window(self, table_size=(4,4)):
        app = self.app
        t = tk.Toplevel(app.master)
        t.wm_title("Craft")
        
        inventory = app.inventory
        self.inventory = app.inventory
        g = constants.grid_size
        height = table_size[1]
        width = table_size[0]
        self.table_size = table_size
        self.h=height
        self.g=g
        self.w=width
        self.MAX_ROWS = min(table_size[1]+5,15, len(inventory))
        
        self.frame = tk.Frame(t)
        self.canvas = tk.Canvas(self.frame, height=(self.h*g)+10, width=(self.w*g)+10, background="brown")
        self.frame2 = tk.Frame(t)
        self.inventory_canvas = tk.Canvas(self.frame2, height=(self.MAX_ROWS*g)+10, width=(self.w*g)+10, background="white")
        
        self.frame3 = tk.Frame(t)
        self.DragManager = app.Canvas_Drag_Manager(
            root = t,
            canvases=[self.canvas, self.inventory_canvas], 
            drop_hook=self.craft_drop_hook, 
            drag_hook=self.craft_drag_hook
            )
        self.render_surface()
        self.render_inventory()
        self.frame3.pack(fill="x", side="bottom")
        self.craft_button = ttk.Button(self.frame3, text="Craft")
        self.craft_button["command"]=self.check_recipe
        self.craft_button.grid(row=0, column=0, columnspan=2, sticky="we")

        self.frame3.pack(fill="x", side="bottom")
        self.frame2.pack(fill=tk.BOTH, expand=1, side="right")
        self.frame.pack(fill=tk.BOTH, expand=1, side="left")

        
    def __init__(self, app):
        self.app = app
        self.load_recipes()