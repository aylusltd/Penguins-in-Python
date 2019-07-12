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
        self.app.sprites.remove(self)
        

    def fire_flee_test(self, app):
        fires = app.screen.fires
        closest_fire_dist = self.fire_fear + 0.1
        closest_fire = None
        flee = False
        directions = []

        for fire in fires:
            d = maps.euclid(x1=self.column, y1=self.row, x2=fire.column, y2=fire.row)
            if d < closest_fire_dist:
                closest_fire_dist = d
                closest_fire = fire
                flee = True
        if flee:
            directions = maps.direction_to_target(self, closest_fire)

        for index, direction in enumerate(directions):
            directions[index] = ~direction

        return closest_fire_dist, directions

    def fire_test(self, app, direction, current_fire_distance=0):
        fires = app.screen.fires
        d_x=0
        d_y=0
        if direction == "self":
            pass
        elif direction == "left":
            d_x = -1
        elif direction == "right":
            d_x = +1
        elif direction == "up":
            d_y = -1
        elif direction == "down":
            d_y = +1
        else:
            raise Exception("Invalid Direction")
            
        for fire in fires:
            d = maps.euclid(x1=self.column + d_x, y1=self.row + d_y, x2=fire.column, y2=fire.row)
            if d <= self.fire_fear and d <= current_fire_distance:
                return False
        return True

    def on_clock_tick(self, tick):
        self.moved = False
        self.move(app=self.app)

    def move(self, app):
        g = constants.grid_size
        not_moved = True
        d_y = self.row - app.tux.row
        d_x = self.column - app.tux.column
        grid = app.screen.grid
        distance, flee_direction = self.fire_flee_test(app=app)
        tux_direction = maps.direction_to_target(source=self, target=app.tux)
        move_directions = []
        current_square = grid[self.row][self.column]        

        if len(flee_direction) > 0:
            move_directions = flee_direction
        elif len(tux_direction) > 0:
            move_directions = tux_direction
        
        for move_direction in move_directions:
            if (
                self.fire_test(app=app, direction=move_direction, current_fire_distance=distance) and
                self.moved == False
                ):
                self.moved = True
                if current_square.neighbor_is(direction=move_direction, allowed_types=["grass"]):
                    delta = maps.move(move_direction, 1)
                    
                    grid[self.row][self.column].occupied = False
                    grid[self.row][self.column].has_monster = False
                    self.row += delta["y"]
                    self.column += delta["x"]
                    app.screen.canvas.move(self.sprite,delta["x"] * g, delta["y"] * g)
                    grid[self.row][self.column].occupied = True
                    grid[self.row][self.column].has_monster = True
                    
                elif current_square.neighbor_has_tux(direction=move_direction):
                    print("tux hit!")
                    print("")
                    app.tux.hit(10)
                else:
                    self.moved = False
                