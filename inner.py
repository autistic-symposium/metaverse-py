#!/usr/bin/python3

#######################################################################
#############
#############           Inner Figures from the Metaverse
#############
#############                   by Mia von Steinkirch
#############
#############                        main.py
#############
#######################################################################

import os
import util

from random import choice, random
from PIL import Image as im


## Constants 
## TODO: add them to an evn file
FIGURES = ['jack_dorsey']
DEFAULT_FONT = ""
BGFOLDER = "background"
FGFOLDER = "foreground"
OUTFOLDER = "."
BLUR = 10
OVERSAMPLE = 1.8
SHIFT_RATIO = 0.3
LEFT_TO_RIGHT = False
DOT_OVER_PATTERN_PROBABILITY = 0.3
WALL = False
FORCE_DEPTH = 0.4
PATTERN_FRACTION = 8.0
CANVAS_SIZE = (1280, 1024)
COLOR_SHOPIFY = [(13, 200, 70), (122, 10, 70), (90, 200, 255)]
COLORMAP = [(176, 224, 230)]


def make_stereogram(depthmap, pattern, color):
    dm_img = util.load_file(depthmap)
    dm_img = util.redistribute_grays(dm_img, FORCE_DEPTH)

    pattern_width = int((dm_img.size[0]/PATTERN_FRACTION))
    canvas_img = im.new(mode="RGB", size=(dm_img.size[0] + pattern_width, dm_img.size[1]), color=color)
    pattern_strip_img = im.new(mode="RGB", size=(pattern_width, dm_img.size[1]), color=(0, 0, 0))
    pattern_raw_img = util.load_file(pattern)
    p_w = pattern_raw_img.size[0]
    p_h = pattern_raw_img.size[1]

    pattern_raw_img = pattern_raw_img.resize((pattern_width, (int)((pattern_width * 1.0 / p_w) * p_h)), im.LANCZOS)
    region = pattern_raw_img.crop((0, 0, pattern_raw_img.size[0], pattern_raw_img.size[1]))
    y = 0

    while y < pattern_strip_img.size[1]:
                pattern_strip_img.paste(region, (0, y, pattern_raw_img.size[0], y + pattern_raw_img.size[1]))
                y += pattern_raw_img.size[1]

            # Oversample. Smoother results.
    dm_img = dm_img.resize(((int)(dm_img.size[0] * OVERSAMPLE), (int)(dm_img.size[1] * OVERSAMPLE)))
    canvas_img = canvas_img.resize(((int)(canvas_img.size[0] * OVERSAMPLE), (int)(canvas_img.size[1] * OVERSAMPLE)))
    pattern_strip_img = pattern_strip_img.resize(((int)(pattern_strip_img.size[0] * OVERSAMPLE), (int)(pattern_strip_img.size[1] * OVERSAMPLE)))
    pattern_width = pattern_strip_img.size[0]

    def shift_pixels(dm_start_x, depthmap_image_object, canvas_image_object, direction):
        depth_factor = pattern_width * SHIFT_RATIO
        cv_pixels = canvas_image_object.load()
        while 0 <= dm_start_x < dm_img.size[0]:
            for dm_y in range(depthmap_image_object.size[1]):
                constrained_end = max(0, min(dm_img.size[0]-1, dm_start_x + direction * pattern_width))
                for dm_x in range(int(dm_start_x), int(constrained_end), direction):
                    dm_pix = dm_img.getpixel((dm_x, dm_y))
                    px_shift = int(dm_pix/255.0*depth_factor*(1 if WALL else -1))*direction
                    if direction == 1:
                        cv_pixels[dm_x + pattern_width, dm_y] = canvas_img.getpixel((px_shift + dm_x, dm_y))
                    if direction == -1:
                        cv_pixels[dm_x, dm_y] = canvas_img.getpixel((dm_x + pattern_width + px_shift, dm_y))

            dm_start_x += direction*pattern_strip_img.size[0]

    dm_center_x = dm_img.size[0]/2
    canvas_img.paste(pattern_strip_img, (int(dm_center_x), 0, int(dm_center_x + pattern_width), canvas_img.size[1]))
    if not WALL:
        canvas_img.paste(pattern_strip_img, (int(dm_center_x - pattern_width), 0, int(dm_center_x), canvas_img.size[1]))
    shift_pixels(dm_center_x, dm_img, canvas_img, 1)
    shift_pixels(dm_center_x + pattern_width, dm_img, canvas_img, -1)

    if pattern:
        canvas_img = canvas_img.resize(((int)(canvas_img.size[0] / OVERSAMPLE), (int)(canvas_img.size[1] / OVERSAMPLE)), im.LANCZOS)  # NEAREST, BILINEAR, BICUBIC, LANCZOS

    return canvas_img


def main():

    for n, fig in enumerate(FIGURES):

        depthmap = os.path.join(BGFOLDER, 'b_{}.png'.format(fig))
        pattern = os.path.join(FGFOLDER, 'f_{}.png'.format(fig))
        outfile = os.path.join(OUTFOLDER, '{}.png'.format(fig))
        color = COLORMAP[n]

        util.save_to_file(make_stereogram(depthmap, pattern, color), outfile)


if __name__ == "__main__":
    main()
