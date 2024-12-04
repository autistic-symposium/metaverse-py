#######################################################################
#############           Inner Figures from the Metaverse
#############                   by bt3gl
#############                   images.py
#######################################################################


import re
import codecs
from PIL import Image as im

import src.utils as utils


def hex_color_to_tuple(s):
    """Convert a hex color string to a tuple of RGB values."""

    if not re.search(r'^#?(?:[0-9a-fA-F]{3}){1,2}$', s):
        return (0, 0, 0)
    
    if len(s) == 3:
        s = "".join(["{}{}".format(c, c) for c in s])

    return tuple(int(c) for c in codecs.decode(s, 'hex'))


def redistribute_grays(img_object, gray_height):
    """Redistribute the grays in an image to a given height."""

    # Convert to grayscale if necessary
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

    # Find the min and max grays
    for x in range(img_object.size[0]):
        for y in range(img_object.size[1]):
            this_gray = img_object.getpixel((x, y))
            if this_gray > img_object.getpixel(max_gray["point"]):
                max_gray["point"] = (x, y)
                max_gray["value"] = this_gray
            if this_gray < img_object.getpixel(min_gray["point"]):
                min_gray["point"] = (x, y)
                min_gray["value"] = this_gray

    # Redistribute the grays
    old_min = min_gray["value"]
    old_max = max_gray["value"]
    old_interval = old_max - old_min
    new_min = 0
    new_max = int(255.0 * gray_height)
    new_interval = new_max - new_min
    conv_factor = float(new_interval) / float(old_interval)
    
    # Convert the image
    pixels = img_object.load()
    for x in range(img_object.size[0]):
        for y in range(img_object.size[1]):
            pixels[x, y] = int((pixels[x, y] * conv_factor)) + new_min
    
    return img_object



def make_stereogram(color, depthmap, pattern, env_vars):
    """Create a stereogram from a depthmap and a pattern."""

    # get environment variables
    force_depth = int(env_vars["FORCE_DEPTH"])
    pattern_fraction = float(env_vars["PATTERN_FRACTION"])
    oversample = int(env_vars["OVERSAMPLE"])
    shift_ratio = float(env_vars["SHIFT_RATIO"])
    wall = int(env_vars["WALL"])
    
    # load images and set up canvas
    dm_img = utils.load_file(depthmap)
    dm_img = redistribute_grays(dm_img, force_depth)
    pattern_width = int((dm_img.size[0]/pattern_fraction))
    canvas_img = im.new(mode="RGB", size=(dm_img.size[0] + pattern_width, dm_img.size[1]), 
                                                                            color=color)
    pattern_strip_img = im.new(mode="RGB", size=(pattern_width, dm_img.size[1]), 
                                                                        color=(0, 0, 0))
    pattern_raw_img = utils.load_file(pattern)
    p_w = pattern_raw_img.size[0]
    p_h = pattern_raw_img.size[1]
    pattern_raw_img = pattern_raw_img.resize((pattern_width, 
                                        (int)((pattern_width * 1.0 / p_w) * p_h)), im.LANCZOS)
    region = pattern_raw_img.crop((0, 0, pattern_raw_img.size[0], pattern_raw_img.size[1]))
    
    # define variables for oversampling
    y = 0
    while y < pattern_strip_img.size[1]:
        pattern_strip_img.paste(region, (0, y, pattern_raw_img.size[0], y + pattern_raw_img.size[1]))
        y += pattern_raw_img.size[1]

    # oversample and omoother results.
    dm_img = dm_img.resize(((int)(dm_img.size[0] * oversample), (int)(dm_img.size[1] * oversample)))
    canvas_img = canvas_img.resize(((int)(canvas_img.size[0] * oversample), 
                                                (int)(canvas_img.size[1] * oversample)))
    pattern_strip_img = pattern_strip_img.resize(((int)(pattern_strip_img.size[0] * oversample),
                                                 (int)(pattern_strip_img.size[1] * oversample)))
    pattern_width = pattern_strip_img.size[0]

    def shift_pixels(dm_start_x, depthmap_image_object, canvas_image_object, direction):
        """Shift pixels in the canvas image based on the depthmap image."""
        
        depth_factor = pattern_width * shift_ratio
        cv_pixels = canvas_image_object.load()
        
        while 0 <= dm_start_x < dm_img.size[0]:
            
            for dm_y in range(depthmap_image_object.size[1]):
                constrained_end = max(0, min(dm_img.size[0]-1,
                                        dm_start_x + direction * pattern_width))
                
                for dm_x in range(int(dm_start_x), int(constrained_end), direction):
                    dm_pix = dm_img.getpixel((dm_x, dm_y))
                    px_shift = int(dm_pix / 255.0*depth_factor*(1 if wall else - 1)) * direction
                    if direction == 1:
                        cv_pixels[dm_x + pattern_width, dm_y] = \
                                        canvas_img.getpixel((px_shift + dm_x, dm_y))
                    if direction == -1:
                        cv_pixels[dm_x, dm_y] = \
                                        canvas_img.getpixel((dm_x + pattern_width + px_shift, dm_y))

            dm_start_x += direction*pattern_strip_img.size[0]

    # shift pixels
    dm_center_x = dm_img.size[0] / 2
    canvas_img.paste(pattern_strip_img, (int(dm_center_x), 0, 
                            int(dm_center_x + pattern_width), canvas_img.size[1]))
    
    # if wall, shift pixels in the other direction
    if not wall:
        canvas_img.paste(pattern_strip_img, (int(dm_center_x - pattern_width), 0, 
                                            int(dm_center_x), canvas_img.size[1]))
    
    shift_pixels(dm_center_x, dm_img, canvas_img, 1)
    shift_pixels(dm_center_x + pattern_width, dm_img, canvas_img, -1)

    # resize back to original size
    if pattern:
        canvas_img = canvas_img.resize(((canvas_img.size[0] / oversample), 
                                        (canvas_img.size[1] / oversample)), im.LANCZOS)  

    return canvas_img
