#!/usr/local/bin/python
from PIL import Image, ImageTk
from os import listdir, rename
from os.path import isfile, join, realpath, dirname, exists, makedirs
from importlib import machinery

def scripts_generator(my_path):
    for f in listdir(my_path):
        if isfile(join(my_path,f)):
            if f.endswith('.py') or f.endswith('.yaml'):
                yield f
def file_generator(my_path):
    for f in listdir(my_path):
        if isfile(join(my_path,f)):
            if f.endswith('.gif') or f.endswith('.png'):
                yield f
def main():
    mypath = dirname(realpath(__file__))
    # print(mypath)
    constants = machinery.SourceFileLoader('constants', mypath+'/../constants.py')
    constants = constants.load_module()

    g = constants.grid_size

    for img in file_generator(mypath):
        full_path = join(mypath,img)
        output_folder = join(mypath, img[:-4].capitalize())
        if not exists(output_folder):
            makedirs(output_folder)

        # print(full_path)
        im = Image.open(full_path)
        new_name = 'sm_' + img[:-3]+'gif'

        if img.endswith('.png'):
            # convert to gif
            if im.mode == 'P':
                transparency = im.info['transparency']

            elif im.mode == 'RGBA' or im.mode == 'LA':
                alpha = im.getchannel('A')
                # Convert the image into P mode but only use 255 colors in the palette out of 256
                im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)

                # Set all pixel values below 128 to 255 , and the rest to 0
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

                # Paste the color of index 255 and use alpha as a mask
                im.paste(255, mask)

                # The transparency index is 255
                im.info['transparency'] = 255
        
        # Resize
        im.thumbnail((g,g), Image.ANTIALIAS)

        # Save Thumbnail for use in game
        im.save(join(mypath,'sm_'+new_name))

    for script in scripts_generator(mypath):
        full_path = join(mypath,img)
        output_folder = join(mypath, img[:-4].capitalize())

        if not exists(output_folder):
            makedirs(output_folder)

        rename(full_path, output_folder+script)

if __name__ == '__main__':
    main()
