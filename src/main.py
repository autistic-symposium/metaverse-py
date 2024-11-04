#!/usr/bin/python3
#######################################################################
#############           Inner Figures from the Metaverse
#############                   by bt3gl
#############                    main.py
#######################################################################

import os
import src.utils as utils
import src.images as images


def main():

    env_vars = utils.load_config()
    figures = env_vars['FIGURES']
    bgfolder = env_vars['BGFOLDER']
    fgfolder = env_vars['FGFOLDER']
    outfolder = env_vars['OUTFOLDER']


    for n, fig in enumerate(figures):

        color = env_vars['COLOR'][n]
        depthmap = os.path.join(bgfolder, f'b_{}.png', fig)
        pattern = os.path.join(fgfolder, f'f_{}.png', fig)
        this_image = images.make_stereogram(color, depthmap, pattern, env_vars)

        outfile = os.path.join(outfolder, f'{}.png', fig)
        utils.save_to_file(this_image, outfile)


if __name__ == "__main__":
    main()
