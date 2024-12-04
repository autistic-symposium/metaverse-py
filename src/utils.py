#######################################################################
#############           Inner Figures from the Metaverse
#############                   by bt3gl
#############                   utils.py
#######################################################################


import os
from pathlib import Path
from PIL import Image as im
from dotenv import load_dotenv


def load_file(imagefile):
    """Load an image file and return an image object."""
    try:
        return im.open(imagefile)
    except IOError as e:
        print('Could not open {0}: {1}'.format(imagefile, e))
        raise


def save_to_file(image, outfile):
    """Save an image object to a file."""
    try:
        image.save(outfile)
    except IOError as e:
        return "Could not create file '{}': {}".format(outfile, e)


def load_config() -> dict:
    """Load and set environment variables."""

    env_file = Path('.') / '.env'
    if not os.path.isfile(env_file):
        print('Please create an .env file')

    env_vars = {}
    load_dotenv(env_file)

    try:
        env_vars['FIGURES'] = os.getenv("FIGURES")
        env_vars['DEFAULT_FONT'] = os.getenv("DEFAULT_FONT")
        env_vars['BGFOLDER'] = os.getenv("BGFOLDER")
        env_vars['FGFOLDER'] = os.getenv("FGFOLDER")
        env_vars['OUTFOLDER'] = os.getenv("OUTFOLDER")
        env_vars['BLUR'] = os.getenv("BLUR")
        env_vars['OVERSAMPLE'] = os.getenv("OVERSAMPLE")
        env_vars['SHIFT_RATIO'] = os.getenv("SHIFT_RATIO")
        env_vars['LEFT_TO_RIGHT'] = os.getenv("LEFT_TO_RIGHT")
        env_vars['DOT_OVER_PATTERN_PROBABILITY'] = os.getenv("DOT_OVER_PATTERN_PROBABILITY")
        env_vars['WALL'] = os.getenv("WALL")
        env_vars['FORCE_DEPTH'] = os.getenv("FORCE_DEPTH")
        env_vars['PATTERN_FRACTION'] = os.getenv("PATTERN_FRACTION")
        env_vars['CANVAS_SIZE'] = os.getenv("CANVAS_SIZE")
        env_vars['COLOR_SHOPIFY'] = os.getenv("COLOR_SHOPIFY")
        env_vars['COLORMAP'] = os.getenv("COLORMAP")
        
        return env_vars

    except KeyError as e:
        print(f'Cannot extract env variables: {e}. Exiting.')
