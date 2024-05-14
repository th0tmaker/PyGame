# Ilijablaster/exit_portal.py
import pygame as pg
from settings import join, BASE_IMG_DIR, TILE_SIZE


class ExitPortal:
    def __init__(self, game, location):
        # REFERENCE
        self.game = game  # Reference to the Game class to access its attributes & methods

        # LOCATION (INSIDE LEVEL MATRIX)
        self.location = location  # Current exit portal location based on row and column indices

        # HITBOX (The definition of a (rect) represents the tangible presence of the object within the program))
        self.rect = None  # Exit portal rect object

        # IMAGE PATH FILES
        self.exit_portal_image_paths = {
            'closed': join(BASE_IMG_DIR, 'exit_portal', 'ep_closed.png'),
            'open1': join(BASE_IMG_DIR, 'exit_portal', 'ep_open1.png'),
            'open2': join(BASE_IMG_DIR, 'exit_portal', 'ep_open2.png')
        }

        # IMAGE
        self.image_path = None  # Define variable that stores the path to the image file for the exit portal
        self.image = None  # Define variable for the exit portal's display image

    # This function renders the drawing of the exit portal image dynamically
    def draw(self):
        self.assign_image_path()  # assign the image path for the exit portal

        if self.image_path:
            # Retrieve the image corresponding to the image path from the EXIT_PORTAL_IMAGES dictionary
            self.image = pg.transform.smoothscale(pg.image.load(self.exit_portal_image_paths[self.image_path]),
                                                  (TILE_SIZE, TILE_SIZE)).convert_alpha()

            # Get the rect for the exit portal image from self.image
            self.rect = self.image.get_rect(topleft=(self.location[1] * TILE_SIZE, self.location[0] * TILE_SIZE))
            self.game.window.blit(self.image, self.rect)  # blit the exit portal image onto the game window

    # This function assigns the exit portal's image path based on the status of creeps in the game
    def assign_image_path(self):
        # If there is one or multiple creeps present in the game
        if self.game.creeps:
            self.image_path = 'closed'  # set the image path to the closed exit portal image

        # If there are NO creeps present in the game
        else:
            current_time = pg.time.get_ticks()  # get current time
            blink_time_interval = 1000  # define the interval for the portal blinking effect

            # Check if current time falls within the first half of the blink time interval
            if current_time % (2 * blink_time_interval) < blink_time_interval:
                self.image_path = 'open1'  # if yes, set image path to the first open exit portal image
            else:
                self.image_path = 'open2'  # if no, set image path to the second open exit portal image
