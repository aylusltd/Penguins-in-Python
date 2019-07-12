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


class logger():
    def __init__(self, target=None, default_level=3, levels=None, level=2):
        if type(levels) is list and len(levels)>1:
            self.levels = levels
        else:
            self.levels = ["silent", "normal", "debug" ,"verbose"]
        self.level = level
        self.default_level = default_level
        if target is None:
            self._print = print
            self.print = print
            self.sink=="stdout"
        self.mirror=False
        self.mirror_sink=None

    def log(self, *args, **kwargs):
        message = ""
        message_level=self.default_level
        # print(args)
        if self.level == 0:
            return None
        if len(kwargs)>0:
            args_dict = kwargs
        if len(args)>1:
            raise Exception("Too many unnamed args")
        if len(args)==1:
            message = args[0]
            if "message" in kwargs:
                raise Exception("Unexpected Argument")
        elif "message" in kwargs:
            message=kwargs["message"]
        if "level" in kwargs:
            level = kwargs["level"]
            if int(level) is level and level<len(self.levels):
                message_level=level
            elif level in self.levels:
                message_level=self.levels.index(level)
            message_level = max(message_level,1)
        
        if message_level<=self.level:
            self.print(message)
    def print(*args, **kwargs):
        self._print(*args, **kwargs)
        if self.mirror:
            self.mirror_sink(*args, **kwargs)

    def _file_mirror(*args, **kwargs):
        self._print(*args, **kwargs)
        with open(self.filename, 'w') as myfile:
                j = json.dumps(my_map)
                myfile.write(j)
                myfile.close()

    def set_level(self, level):
        if int(level) is level and level<len(self.levels):
            print("valid level")

        if level is 0 or level==self.levels[0]:
            self.level = 0
        elif level is 1 or level == self.levels[1]:
            self.level = 1

    def mirror_output(self, sink, initial_message="begin mirrored log"):
        if sink == self.sink:
            raise Exception("Cannot Mirror to current output")
        if type(sink) is str:
            pass
        else:
            sink(initial_message)
            self.mirror_sink=sink

    def stop_mirror(self, end_message="end mirrored log"):
        self.print(end_message)
        self.mirror=False
        self.mirror_sink=None
        self.print=self._print


def log(*args, **kwargs):
    log_precedence = ["silent", "normal", "debug" ,"verbose"]
    if len(kwargs) == 0:
        pass
    print("args:")
    for arg in args:
        print(arg)
    print("kwargs")
    for kwarg in kwargs:
        print(kwarg)
        print(kwargs[kwarg])
    if "app" in kwargs:
        app=kwargs["app"]
    if "set_log_level" in kwargs:
        l = kwargs["set_log_level"]
        if l in log_precedence:
            app.log_level = l
        else:
            raise Exception("Invalid Log Level")

    if "level" in kwargs:
        level=kwargs["level"]
    else:
        level="debug"
    log_level = app.log_level
    message_precedence
    if log_level == "debug":
        print("DEBUG")

def l(s,obj):
    o = string.Template(s).substitute(obj)
    print(o)

class app():
    def __init__(self, log_level="debug"):
        self.log_level = log_level

if __name__ == "__main__":
    # a = app()
    # log(level="debug", app=a)
    l = logger()
    l.set_level(2)
    l.log("Hello World")
    l.log("should print", level=1)