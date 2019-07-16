import os
from pathlib import Path
import pyglet
    
class Sound():
    def __init__(self, src):
        self.src = src
        self.loaded = False

    def load(self):
        dir_name = os.path.dirname(self.src) + '/'
        file_name = Path(self.src).name
        print(dir_name)
        # dir_name = ['/Users/jasonnichols/projects/Penguins-in-Python/venv/lib/python3.7/site-packages/pygame/examples/data/']
        if dir_name not in pyglet.resource.path:
            # print('adding dir_name: '+dir_name)
            pyglet.resource.path.append(dir_name)
            pyglet.resource.reindex()
        sound = pyglet.resource.media(file_name, streaming=False)
        self.sound = sound
        self.loaded=True

    def play(self):
        if self.loaded:
            self.sound.play()
        else:
            raise Exception("cannot play sound until loaded")
