#!/usr/local/bin/python
from PIL import Image, ImageTk
from os import listdir
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

mypath = dirname(__file__)
print(mypath)
constants_path = mypath+'../constants.py'
print('constants_path')
print(constants_path)

constants = load_source('constants', constants_path)
g = constants.grid_size

onlyfiles = [f for f in listdir('./') if isfile(f) and "bridge" in f] # and "sm_" not in f]

for img in onlyfiles:
    full_path = join(mypath,img)
    i = Image.open(full_path)
    i.thumbnail((g,g), Image.ANTIALIAS)
    # i=i.resize((g,g), Image.ANTIALIAS)
    i.save(join(mypath,"sm_"+img))
