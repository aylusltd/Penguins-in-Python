#!/usr/local/bin/python
from PIL import Image, ImageTk
from os import listdir
from os.path import isfile, join, realpath, abspath, dirname
from importlib import load_source

mypath = dirname(__file__)
print(mypath)
constants = load_source('constants', mypath+'/../constants.py')
g = constants.grid_size

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and "camp_fire.gif" in f and "sm_" not in f]

for img in onlyfiles:
    full_path = join(mypath,img)
    i = Image.open(full_path)
    i.thumbnail((g,g), Image.ANTIALIAS)
    # i=i.resize((g,g), Image.ANTIALIAS)
    i.save(join(mypath,"sm_"+img))
