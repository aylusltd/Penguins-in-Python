from tkinter import filedialog
import json
import sprites

def load(app, filename=None):
    if filename is None:
        filename=filedialog.askopenfilename(initialdir = "~/Desktop",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    with open(filename, 'rb') as myfile:
        r = myfile.read()
        myfile.close()
    r = json.loads(r)
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
    app.tux = sprites.Sprite(
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


def save(app, filename=None):
    if filename is None:
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
    with open(filename, 'w') as myfile:
        j = json.dumps(f)
        myfile.write(j)
        myfile.close()
