# Snake/sound.py
import time
import pygame as pg

pg.init()
pg.mixer.init(frequency=44100, size=32, channels=2, buffer=512)  # initialize Pygame mixer for sound

# Music (path)
bg_music = "assets/sound/game_theme2.mp3"  # game background music

# Sound effects (paths)
food_pickup_sfx = pg.mixer.Sound("assets/sound/food_pickup_sfx3.ogg")
crash_sfx = pg.mixer.Sound("assets/sound/crash_sfx.ogg")
round_over_sfx = pg.mixer.Sound("assets/sound/game_over_sfx.ogg")


def play_pickup_food_sound():
    # Play sound effect when player object collides with food object
    food_pickup_sfx.play(maxtime=0)
    food_pickup_sfx.set_volume(0.9)


def play_crash_sound():
    # Play sound effect when player object collides with window borders or itself
    crash_sfx.play()
    crash_sfx.set_volume(0.4)

    # Pause the game for 1 sec, play round over sound, pause the game for 3 sec
    time.sleep(1)
    play_round_over_sound()
    time.sleep(3)


def play_round_over_sound():
    # Play sound effect when round is over
    round_over_sfx.play()
    round_over_sfx.set_volume(0.1)


def play_background_music():
    # Play game background music
    pg.mixer.music.load(bg_music)
    pg.mixer.music.play(loops=-1)  # loop back to start when finished
    pg.mixer.music.set_volume(0.4)
