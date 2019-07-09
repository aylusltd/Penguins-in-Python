import random
import string

from PIL import Image, ImageTk

import constants
import maps

class Monster(constants.correction):
    def __init__(self,app, x=None, y=None):
        # constants.l('Placing self',{})
        h = constants.bounds["y"][1]
        w = constants.bounds["x"][1]
        g = constants.grid_size
        cx = int(w/(2*g)+1)
        cy = int(h/(2*g))
        img = Image.open("sprites/sm_monster.gif")

        self.f_sprite = ImageTk.PhotoImage(img)
        self.fire_fear = 3
        original_cx = cx
        s=app.screen.grid[cy][cx]
        tries=0
        MAX_TRIES = 30
        if (x is None) or (y is None):
            while (s.square_type is not "grass" or s.occupied is True) and (tries < MAX_TRIES):
                old_cx = cx
                old_cy = cy
                if cx<(w/g)-2:
                    cx+=random.randint(-6,5)
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
            s.has_monster=True
            self.app = app
            self.type = "virus"
            self.placed = True
            self.moved = False
        else: 
            print("Tries exceeded")
            self.placed = False
    def destroy(self):
        self.app.screen.canvas.delete(self.sprite)
        self.app.screen.grid[self.row][self.column].occupied = False
        self.app.screen.grid[self.row][self.column].has_monster = False

        self.app.screen.monsters.remove(self)
    def fire_test(self, app, direction):
        fires = app.screen.fires
        d_x=0
        d_y=0
        if direction == "left":
            d_x = -1
        if direction == "right":
            d_x = +1
        if direction == "up":
            d_y = -1
        if direction == "down":
            d_y = +1
        for fire in fires:
            d = maps.euclid(x1=self.column + d_x, y1=self.row + d_y, x2=fire.column, y2=fire.row)
            if d < self.fire_fear:
                return False
        return True
    def move(self, app):
        g = constants.grid_size
        not_moved = True
        d_y = self.row - app.tux.row
        d_x = self.column - app.tux.column
        grid = app.screen.grid
        try:
            if abs(d_x) < abs(d_y):
                if d_y < 0:
                    if (
                        grid[self.row+1][self.column].square_type == "grass" and
                        self.fire_test(app=app, direction="down")
                        ):
                        if not grid[self.row+1][self.column].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_monster = False
                        
                            app.screen.canvas.move(self.sprite,0,g)
                            self.row+=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_monster = True

                            not_moved=False
                            self.moved=True
                        elif ( app.tux.row == self.row+1 and 
                               app.tux.column == self.column):
                            self.moved=True
                            not_moved=False                    
                            app.tux.hit(1)
                        else:
                            # pass
                            pass

                elif d_y > 0:
                    if (
                        grid[self.row-1][self.column].square_type == "grass" and
                        self.fire_test(app=app, direction="up")
                        ):
                        if not grid[self.row-1][self.column].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_monster = False

                            app.screen.canvas.move(self.sprite,0,-g)
                            self.row-=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_monster = True

                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row-1 and 
                               app.tux.column == self.column):
                            self.moved=True
                            not_moved=False
                            app.tux.hit(1)
                        else:
                            pass
            if not_moved:
                if d_x < 0:
                    if (
                        grid[self.row][self.column+1].square_type == "grass" and
                        self.fire_test(app=app, direction="right")
                        ):
                        if not grid[self.row][self.column+1].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_monster = False

                            app.screen.canvas.move(self.sprite,g,0)
                            self.column+=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_monster = True

                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row and 
                            app.tux.column == self.column + 1):                        
                            self.moved=True
                            not_moved=False
                            app.tux.hit(1)
                        else:
                            pass
                elif d_x > 0:
                    if (
                        grid[self.row][self.column-1].square_type == "grass" and
                        self.fire_test(app=app, direction="left")
                        ):
                        if not grid[self.row][self.column-1].occupied:
                            grid[self.row][self.column].occupied = False
                            grid[self.row][self.column].has_monster = False

                            app.screen.canvas.move(self.sprite,-g,0)
                            self.column-=1
                            grid[self.row][self.column].occupied = True
                            grid[self.row][self.column].has_monster = True
                            self.moved=True
                            not_moved=False
                        elif ( app.tux.row == self.row and 
                            app.tux.column == self.column - 1):
                            self.moved=True
                            not_moved=False
                            app.tux.hit(1)
                        else:
                            pass
        except IndexError:
            pass