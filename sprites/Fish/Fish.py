import constants
import random
import string
from os.path import dirname

from PIL import Image, ImageTk
# from os.path import isfile, join, realpath, abspath, dirname
# from imp import load_source
mypath = dirname(__file__)

class Fish(constants.correction):
    def __init__(self,app, x=None, y=None):
        # constants.l('Placing self',{})
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        cx = int(w/(2*g)+1)
        cy = int(h/(2*g))
        img = Image.open(mypath + "/sm_fish.gif")

        self.f_sprite = ImageTk.PhotoImage(img)
        original_cx = cx
        s=app.screen.grid[cy][cx]
        tries=0
        MAX_TRIES = 30
        if (x is None) or (y is None):
            while (s.square_type is not "water" or s.occupied is True) and (tries < MAX_TRIES):
                # constants.l('Moving from {x:$x, y:$y}', {'x':cx,'y':cy})
                old_cx = cx
                old_cy = cy
                if cx<(w/g)-2:
                    cx+=random.randint(-6,5)
                # else:
                    # cx=original_cx
                    cy+=random.randint(-4,4)
                tries+=1
                try:
                    s=app.screen.grid[cy][cx]
                except IndexError:
                    cx = old_cx
                    cy = old_cy

        else:
            cx = x
            cy = y
        if tries < MAX_TRIES:
            s=app.screen.grid[cy][cx]
            self.sprite = app.screen.canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.f_sprite)
            self.row=cy
            self.column=cx
            s.occupied=True
            s.has_fish=True
            self.app = app
            self.type = "fish"
            self.placed = True
            self.moved = False
        else: 
            print("Tries exceeded")
            self.placed = False
    def destroy(self):
        self.app.screen.canvas.delete(self.sprite)
        self.app.screen.grid[self.row][self.column].occupied = False
        self.app.screen.grid[self.row][self.column].has_fish = False

        self.app.screen.fishes.remove(self)
        self.app.sprites.remove(self)
    
    def on_clock_tick(self, tick):
        self.moved = False
        self.move(app=self.app)

    def move(self, app):
        # self.moved=True
        g = constants.grid_size
        not_moved = True
        d_y = self.row - app.tux.row
        d_x = self.column - app.tux.column
        grid = app.screen.grid
        try:
            if abs(d_x) > abs(d_y):
                if d_y > 0:
                    if grid[self.row+1][self.column].square_type == "water":
                        if not grid[self.row+1][self.column].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_fish = False
                        
                            app.screen.canvas.move(self.sprite,0,g)
                            self.row+=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_fish = True

                            not_moved=False
                            self.moved=True
                        elif ( app.tux.row == self.row+1 and 
                               app.tux.column == self.column):
                            self.moved=True
                            not_moved=False                    
                        else:
                            # pass
                            pass

                elif d_y < 0:
                    if grid[self.row-1][self.column].square_type == "water":
                        if not grid[self.row-1][self.column].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_fish = False

                            app.screen.canvas.move(self.sprite,0,-g)
                            self.row-=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_fish = True

                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row-1 and 
                               app.tux.column == self.column):
                            self.moved=True
                            not_moved=False
                        else:
                            # pass
                            pass
            if not_moved:
                if d_x > 0:
                    if grid[self.row][self.column+1].square_type == "water":
                        if not grid[self.row][self.column+1].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_fish = False

                            app.screen.canvas.move(self.sprite,g,0)
                            self.column+=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_fish = True

                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row and 
                            app.tux.column == self.column + 1):                        
                            self.moved=True
                            not_moved=False
                        else:
                            pass
                elif d_x < 0:
                    if grid[self.row][self.column-1].square_type == "water":
                        if not grid[self.row][self.column-1].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_fish = False

                            app.screen.canvas.move(self.sprite,-g,0)
                            self.column-=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_fish = True
                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row and 
                            app.tux.column == self.column - 1):
                            self.moved=True
                            not_moved=False
                        else:
                            pass
        except IndexError:
            pass