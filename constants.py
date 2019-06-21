import string

class correction():
    def __getitem__(self, name):
        return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    def __delitem__(self, name):
        return delattr(self, name)
    def __contains__(self, name):
        return hasattr(self, name)

grid_size = 40
INTERVAL  = 20

bounds = {
    "x": [0,1000],
    "y": [0,720]
}

def l(s,obj):
    o = string.Template(s).substitute(obj)
    print(o)