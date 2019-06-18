#!/usr/local/bin/python
from PIL import Image, ImageTk
from os import listdir
from os.path import isfile, join, realpath, abspath, dirname
from imp import load_source

mypath = dirname(__file__)
print mypath
constants = load_source('constants', mypath+'/../constants.py')
g = constants.grid_size

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and "rock.png" in f and "sm_" not in f]

for img in onlyfiles:
    full_path = join(mypath,img)
    print full_path
    im = Image.open(full_path)
    print im.mode
    print im.info
    new_name = full_path[:-3]+'gif'
    if im.mode == 'P':
        transparency = im.info['transparency'] 
        im.save(new_name, transparency=transparency)
    elif im.mode == 'RGBA':
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        im.save(new_name)
    elif im.mode == 'LA':
        im = im.convert('RGBA').convert('P', palette=Image.ADAPTIVE)
        im.save(new_name)
    
