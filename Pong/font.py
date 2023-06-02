# Pong/font.py
from setup import pg, setup_pygame

setup_pygame()  # initialize pygame module to access pg.font.Font

# font (paths)
menu_font = "Pong/font/Menu.ttf"
score_font = "Pong/font/Score.ttf"
countdown321_font = "Pong/font/Countdown321.ttf"

# texts
menu_txt = pg.font.Font(menu_font, 22)
score_txt = pg.font.Font(score_font, 36)
countdown321_txt = pg.font.Font(countdown321_font, 30)
