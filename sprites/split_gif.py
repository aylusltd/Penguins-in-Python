import os
from PIL import Image


def extractFrames(inGif, outFolder):
    frame = Image.open(inGif)
    nframes = 0
    while frame:
        frame.save( '%s/%s-%s.gif' % (outFolder, os.path.basename(inGif)[:-4], nframes ) , 'GIF')
        nframes += 1
        try:
            frame.seek( nframes )
        except EOFError:
            break;
    return True
    

extractFrames('snore.gif', 'snore')