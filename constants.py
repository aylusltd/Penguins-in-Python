import string
import linecache
import os
import tracemalloc

def display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

class correction():
    def __getitem__(self, name):
        return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    def __delitem__(self, name):
        return delattr(self, name)
    def __contains__(self, name):
        return hasattr(self, name)

# Tech Debt
class Direction(correction):
    def __init__(self, val):
        east_names = ["right", "r", "east", "e"]
        west_names = ["left", "l", "west", "w"]
        north_names = ["up", "u", "north", "n"]
        south_names = ["south", "d", "south", "s"]

        if val in west_names:
            val = "left"
        elif val in east_names:
            val = "right"
        elif val in north_names:
            val = "up"
        elif val in south_names:
            val = "down"
        else:
            raise Exception("Invalid Direction")

        self.val = val

    def __invert__(self):
        new_dir_name = ""
        if self.val == "left":
            new_dir_name = "e"
        elif self.val == "right":
            new_dir_name = "w"
        elif self.val == "up":
            new_dir_name = "s"
        elif self.val == "down":
            new_dir_name = "n"
        else:
            raise Exception("Invalid Direction")

        new_direction = Direction(new_dir_name)
        return new_direction

    def __str__(self):
        # print("Direction to String!")
        return self.val

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

NORTH = Direction("north")
SOUTH = Direction("south")
EAST = Direction("east")
WEST = Direction("west")

grid_size = 40
INTERVAL  = 20

bounds = {
    "x": [0,1000],
    "y": [0,720]
}
