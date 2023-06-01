# Pong/setup.py
import pygame as pg
from constants import WINDOW_SIZE, FPS


def setup_pygame():
    pg.init()  # initialize Pygame


def setup_mixer():
    pg.mixer.init(frequency=44100, size=32, channels=2, buffer=512)  # Initialize Pygame mixer for sound


def access_window():
    # Create window display, caption & icon
    window_ = pg.display.set_mode(WINDOW_SIZE)
    pg.display.set_caption("Pong | by Ilija")
    pg.display.set_icon(pg.image.load("C:/Users/krasn/PycharmProjects/My_Projects/PyGame/Pong/icon/pong.ico"))

    return window_  # return window


def access_clock():
    clock_ = pg.time.Clock()  # Create instance of game clock to control display framerate

    return clock_  # return clock


clock = access_clock()  # create our clock to use in render_display()


def render_display():
    pg.display.flip()  # update/refresh display window
    clock.tick(FPS)  # set consistent display window framerate to avoid inconsistent gameplay speed/performance
