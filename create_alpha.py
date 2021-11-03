import traceback
import sys

from PIL import Image


arg = sys.argv

if len(arg) <= 2:
    exit("usage: python create_alpha.py [image path] [save path]")
else:
    fname = arg[1]
    sname = arg[2]
    try:
        a = Image.open(fname)
    except FileNotFoundError:
        traceback.print_exc()
        exit()

    image = Image.new("RGBA", (a.width, a.height), (255, 255, 255, 0))
    for x in range(a.width):
        for y in range(a.height):
            p = a.getpixel((x, y))
            if p[0] != 255 and p[1] != 255 and p[2] != 255:
                image.putpixel((x, y), p)

    image.save(sname)
