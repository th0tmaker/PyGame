# Snake/font.py
import pygame as pg

pg.init()

# Font (paths)
main_font = "assets/font/nokia_cell.ttf"

# Game texts
space_txt = pg.font.Font(main_font, 22)
score_txt = pg.font.Font(main_font, 21)

