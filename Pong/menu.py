# Pong/menu.py
import pygame as pg
from constants import WINDOW_SIZE, LIMED_SPRUCE, WHITE, SUNSET_ORANGE
from setup import access_window
from font import menu_txt

window = access_window()  # access game window


# Create a class that will handle the general code for the game master/main menu
class MasterMenu:
    def __init__(self):
        self.mastermenu_selections = ["New Game", "Quit"]
        self.mastermenu_colors = [WHITE] * len(self.mastermenu_selections)
        self.mastermenu_rects = []

    def display(self, surface, events):
        window.fill(LIMED_SPRUCE)  # fill window background

        # Define each main menu selection as rendered text with its own rectangle
        for selection in self.mastermenu_selections:
            text_surface = menu_txt.render(selection, True, WHITE)  # render text
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 +  # create text rect
                                                      (self.mastermenu_selections.index(selection) - 1) * 50))
            self.mastermenu_rects.append(text_rect)  # append the rect to its own list
            surface.blit(text_surface, text_rect)  # draw the text surface and rect on the window

        # Check for main menu events
        for event in events:
            # Check to detect mouse motion
            if event.type == pg.MOUSEMOTION:
                # Iterate through each main menu rect and color
                for rect, color in zip(self.mastermenu_rects, self.mastermenu_colors):
                    # If rect collides with event(MOUSEMOTION) mouse cursor position
                    if rect.collidepoint(event.pos):
                        # color of rect at index that is hovered turns SUNSET_ORANGE
                        self.mastermenu_colors[self.mastermenu_rects.index(rect)] = SUNSET_ORANGE
                    else:
                        # else color of rect at index that not hovered is WHITE
                        self.mastermenu_colors[self.mastermenu_rects.index(rect)] = WHITE

        # Iterate through all the lists again and draw their text selection, rect and color
        for selection, color, rect in zip(self.mastermenu_selections, self.mastermenu_colors, self.mastermenu_rects):
            text_surface = menu_txt.render(selection, True, color)
            window.blit(text_surface, rect)

    # Check if mouse click occurs within the bounds of the selection rect
    def handle_mouse_click(self, mouse_pos):
        # For every rect in main menu rects
        for rect in self.mastermenu_rects:
            # If rect collided with mouse cursor position
            if rect.collidepoint(mouse_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                # Return the index of hovered rect
                return self.mastermenu_rects.index(rect)
            else:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        # Otherwise, if no rect hoevered, return no value
        return None


# Create instance of MasterMenu class for the game menu
menu = MasterMenu()
