# Ilijablaster/settings.py
from os.path import join as join

# Window resolution
WINDOW_SIZE = (1392, 624)

# Display framerate
FPS = 120

# Dir paths
BASE_IMG_DIR = join('assets', 'images')
BASE_FONT_DIR = join('assets', 'fonts')
BASE_ICON_DIR = join('assets', 'icon')
BASE_AUDIO_DIR = join('audio')

# Grid
TILE_SIZE = 48

# Control keys
ALPHABET_INPUT_KEYS = [chr(i) for i in range(ord('a'), ord('z') + 1)]
OTHER_INPUT_KEYS = ['space', 'lctrl', 'rctrl', 'lshift', 'rshift', 'lalt', 'ralt', 'up', 'down', 'left',
                    'right', 'kp0', 'kp1', 'kp2', 'kp3', 'kp4', 'kp5', 'kp6', 'kp7', 'kp8', 'kp9']

# Game variables
IMPASSABLE_CELLS = {0, 2, 5, 6, 7, 9}

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
BLUE = (0, 150, 255)
DARKBLUE = (0, 0, 231)
RED = (255, 0, 0)
REDBROWN = (140, 0, 2)
GREY = (69, 88, 89)
BG = (217, 196, 183)
COFFEE = (111, 78, 55)
ORANGE = (223, 97, 36)
