# Pong/sound.py
from setup import pg, setup_mixer

setup_mixer()  # initialize pygame mixer module to access pg.mixer.Sound()

# music (paths)
menu_music = "sound/menu_theme.mp3"
game_music = "sound/game_theme.mp3"

# sound effects
countdown321_sfx = pg.mixer.Sound("sound/countdown_sfx.ogg")
paddle_strike_sfx = pg.mixer.Sound("sound/paddle_strike_sfx.ogg")
point_scored_sfx = pg.mixer.Sound("sound/point_scored_sfx.ogg")


def play_menu_music():
    # Play menu theme music
    pg.mixer.music.load(menu_music)
    pg.mixer.music.play(loops=-1)
    pg.mixer.music.set_volume(0.5)


def play_game_music():
    # Play in game theme music
    pg.mixer.music.load(game_music)
    pg.mixer.music.play(loops=-1)
    pg.mixer.music.set_volume(0.2)


def play_countdown321_sound():
    # Play sound effect for final 3 seconds of the round start countdown timer
    countdown321_sfx.play()
    countdown321_sfx.set_volume(0.2)


def play_point_scored_sound():
    # Play sound effect for when a point is scored
    point_scored_sfx.play()
    point_scored_sfx.set_volume(0.4)


def play_paddle_strike_sound():
    # Play sound effect for when a paddles strikes the ball
    paddle_strike_sfx.play(maxtime=0)
    paddle_strike_sfx.set_volume(0.5)
