import re
import sys

from PIL import Image
import numpy as np

class Pic_Data():
    def __init__(self, rgb, transparency, mask):
        self.mask = mask
        self.data = rgb
        self.transparency = transparency

def pic_to_array(source):
    pic = Image.open(source)
    transparency = pic.info['transparency'] 
    pic = pic.convert('RGBA')
    alpha = pic.getchannel('A')
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
    pix = np.array(pic)
    my_pic = Pic_Data(rgb=pix, transparency=transparency, mask=mask)
    return my_pic

def swap_channels(arr, a,b):
    temp_arr = np.copy(arr)
    temp_arr[:,:,a] = np.copy(arr[:,:,b])
    temp_arr[:,:,b] = np.copy(arr[:,:,a])
    return temp_arr

def save_image(source, transform, pic):
    size = pic.data.shape
    print('shape: ')
    # print(size)
    print('image 2 write')
    l = []
    for row in pic.data:
        for pixel in row:
            t = (pixel[0], pixel[1], pixel[2])
            l.append(t)
    # data = list(tuple(pixel) for pixel in data)
    # print(l)
    new_pic = Image.new(mode='RGB', size=(size[1], size[0]))
    new_pic.putdata(l)
    new_pic = new_pic.convert('P', palette=Image.ADAPTIVE, colors=255)
    mask = pic.mask
    new_pic.paste(255, mask)
    new_pic.info['transparency'] = 255
    new_pic.save(source[:-4] + '_' +transform + '.gif')

def white_to_black(source):
    threshhold = 250
    alpha_threshhold = 128
    for row in source:
        for pixel in row:
            if ( 
                pixel[0] >= threshhold and
                pixel[0] >= threshhold and
                pixel[0] >= threshhold and
                pixel[3] > alpha_threshhold
                ):
                pixel[0] = pixel[1] = pixel[2] = 0
    return source


def swap_from_str(source, my_str):
    # acceptable strings R2B, G2R, etc
    my_str = my_str.upper()
    my_pic = pic_to_array(source)
    print(my_str)
    if my_str != 'W2B':
        assert re.match('^[RGBA]2[RGBA]$', my_str) is not None
        color_str = 'RGBA'
        a = color_str.index(my_str[0])
        print('a')
        print(a)
        b = color_str.index(my_str[2])
        print('b')
        print(b)
        my_pic.data = swap_channels(my_pic.data, a, b)
    else:
        my_pic.data = white_to_black(my_pic.data)
    save_image(source=source, transform=my_str, pic=my_pic)

def main():
    args = sys.argv
    source = args[1]
    print(source)
    color_mode = args[2]
    print(color_mode)
    swap_from_str(source=source, my_str=color_mode)

if __name__ == '__main__':
    main()
    