#!/usr/local/bin/python
from PIL import Image
from os import listdir
from os.path import isfile, join, realpath, dirname
import importlib

mypath = dirname(realpath(__file__))
print(mypath)

constants = importlib.machinery.SourceFileLoader('constants', mypath+'/../constants.py')
constants = constants.load_module()

g = constants.grid_size

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".png")]

for img in onlyfiles:
    full_path = join(mypath,img)
    print(full_path)

    im = Image.open(full_path)
    print(im.mode)
    print(im.info)

    alpha = im.getchannel('A')

    new_name = full_path[:-3]+'gif'
    if im.mode == 'P':
        transparency = im.info['transparency'] 
        im.save(new_name, transparency=transparency)
    elif im.mode == 'RGBA':
        # Convert the image into P mode but only use 255 colors in the palette out of 256
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)

        # Set all pixel values below 128 to 255 , and the rest to 0
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

        # Paste the color of index 255 and use alpha as a mask
        im.paste(255, mask)

        # The transparency index is 255
        im.info['transparency'] = 255
        im.save(new_name)
    elif im.mode == 'LA':
        im = im.convert('RGBA').convert('P', palette=Image.ADAPTIVE)
        im.save(new_name)