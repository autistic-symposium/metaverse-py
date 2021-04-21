#!/usr/bin/python3

#######################################################################
#############
#############           Inner Figures from the Metaverse
#############
#############                   by bt3
#############
#############                   util.py
#############
#######################################################################

import re
import time

from PIL import Image as im
from PIL import ImageFont as imf
from PIL import ImageDraw as imd


def load_file(imagefile):
    try:
        return im.open(imagefile)
    except IOError as e:
        print('Could not open {0}: {1}'.format(imagefile, e))
        raise


def save_to_file(image, outfile):
    try:
        image.save(outfile)
    except IOError as e:
        return "Could not create file '{}': {}".format(outfile, e)


def hex_color_to_tuple(s):
    if not re.search(r'^#?(?:[0-9a-fA-F]{3}){1,2}$', s):
        return (0, 0, 0)
    if len(s) == 3:
        s = "".join(["{}{}".format(c, c) for c in s])
    return tuple(int(c) for c in codecs.decode(s, 'hex'))


def redistribute_grays(img_object, gray_height):
    if img_object.mode != "L":
        img_object = img_object.convert("L")
    min_gray = {
        "point": (0, 0),
    }
    min_gray["value"] = img_object.getpixel(min_gray["point"])
    max_gray = {
        "point": (0, 0),
    }
    max_gray["value"] = img_object.getpixel(max_gray["point"])

    for x in range(img_object.size[0]):
        for y in range(img_object.size[1]):
            this_gray = img_object.getpixel((x, y))
            if this_gray > img_object.getpixel(max_gray["point"]):
                max_gray["point"] = (x, y)
                max_gray["value"] = this_gray
            if this_gray < img_object.getpixel(min_gray["point"]):
                min_gray["point"] = (x, y)
                min_gray["value"] = this_gray

    old_min = min_gray["value"]
    old_max = max_gray["value"]
    old_interval = old_max - old_min
    new_min = 0
    new_max = int(255.0 * gray_height)
    new_interval = new_max - new_min

    conv_factor = float(new_interval)/float(old_interval)

    pixels = img_object.load()
    for x in range(img_object.size[0]):
        for y in range(img_object.size[1]):
            pixels[x, y] = int((pixels[x, y] * conv_factor)) + new_min
    return img_object


def make_depth_text(text, font):
    image = im.new('L', canvas_size, "black")
    font_size = 1
    fnt = imf.truetype(fontpath, font_size)
    while fnt.getsize(text)[0] < canvas_size[0]*0.9 and fnt.getsize(text)[1] < canvas_size[1]*0.9:
        font_size += 1
        fnt = imf.truetype(fontpath, font_size)
    imd.Draw(image).text(
        ((canvas_size[0] / 2 - fnt.getsize(text)[0] / 2, canvas_size[1] / 2 - (fnt.getsize(text)[1] / 2)*1.2)),
        text, font=fnt,
        fill=((int)(255.0)))

    return image
