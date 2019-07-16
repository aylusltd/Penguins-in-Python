# Expanded from https://stackoverflow.com/a/15589291/1168038
# With Iteration from https://stackoverflow.com/a/24377/1168038
# Thanks u/ars, u/Ben Gartner, u/user1783597, and u/the Tin Man

class Dictate(object):
    """Object view of a dict, updating the passed in dict when values are set
    or deleted. "Dictate" the contents of a dict...: """

    def __init__(self, d):
        # since __setattr__ is overridden, self.__dict = d doesn't work
        object.__setattr__(self, '_Dictate__dict', d)
        self.keys = d.keys
        self.current=0
        self._keys = list(d.keys())

    # Fixed for key in Dictate()
    def __iter__(self):
        return self

    def __next__(self): # Python 2: def next(self)
        if self.current >= len(self._keys):
            self.current = 0
            raise StopIteration
        else:
            key = self._keys[self.current]
            self.current += 1
            return key

    # Dictionary-like access / updates
    def __getitem__(self, name):
        value = self.__dict[name]
        if isinstance(value, dict):  # recursively view sub-dicts as objects
            value = Dictate(value)
        return value

    def __setitem__(self, name, value):
        self.__dict[name] = value
    def __delitem__(self, name):
        del self.__dict[name]

    # Object-like access / updates
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        del self[name]

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.__dict)
    def __str__(self):
        return str(self.__dict)