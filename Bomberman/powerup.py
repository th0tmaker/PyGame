# Ilijablaster/powerup.py
import random
import pygame as pg
from settings import join, TILE_SIZE, BASE_IMG_DIR


class PowerUp:
    def __init__(self, game, image_path):
        # REFERENCE
        self.game = game  # Reference to the Game class to access its attributes & methods

        # LOCATION (INSIDE LEVEL MATRIX)
        self.location = None  # Current powerup location based on row and column indices

        # HITBOX (The definition of a (rect) represents the tangible presence of the object within the program))
        self.rect = None  # Powerup rect object

        # IMAGE FILE PATHS
        self.powerup_image_paths = {
            'explosion_radius': {
                'default': join(BASE_IMG_DIR, 'power_ups', 'explosion_radius_pwr.png'),
                'on_ice': join(BASE_IMG_DIR, 'power_ups', 'explosion_radius_pwr_onice.png')
            },
            'extra_bomb': {
                'default': join(BASE_IMG_DIR, 'power_ups', 'extra_bomb_pwr.png'),
                'on_ice': join(BASE_IMG_DIR, 'power_ups', 'extra_bomb_pwr_onice.png')
            }
        }

        # IMAGE
        self.image_path = image_path  # Define variable to store the path to the image file for the powerup
        self.image = None  # Define variable for the powerup's display image
        self.load_image()  # Run function which loads powerup image and creates a rect at class init

    # This function loads the image path of the powerup object to create an image and defines a rect hitbox for it
    def load_image(self):
        # Get powerup's image path from dict, process it, save it into self.image and create a rect object from image
        if self.image_path:
            image_paths = self.powerup_image_paths.get(self.image_path)
            if image_paths:
                image_path = image_paths.get('default')
                if image_path:
                    image = pg.image.load(image_path)
                    if image:
                        self.image = pg.transform.smoothscale(image, (TILE_SIZE, TILE_SIZE)).convert_alpha()
                        self.rect = self.image.get_rect()

    # This function renders the drawing of the powerup image and updates its rect position dynamically
    def draw(self):
        # Extract row and column positions from the powerup's location
        if self.location:
            row, col = self.location
            cell_value = self.game.level.level_matrix[row][col]
            image_paths = self.powerup_image_paths.get(self.image_path, {})  # Retrieve image paths
            # Check if the cell value is 10 (indicating a powerup) and image paths exist
            if cell_value == 10 and image_paths:
                # Check for collision with ice tile and decide image path based on whether the powerup is on ice
                on_ice_tile = any(self.rect.colliderect(ice_tile.rect) for ice_tile in self.game.ice_tiles)
                image_path_key = 'on_ice' if on_ice_tile else 'default'
                image_path = image_paths.get(image_path_key)

                # Load and process the image if the image path is valid
                if image_path:
                    self.image = pg.image.load(image_path)
                    self.image = pg.transform.smoothscale(self.image, (TILE_SIZE, TILE_SIZE)).convert_alpha()

                    # Update the position of the powerup's rect and display the image onto the game window
                    if self.image:
                        self.rect.x = col * TILE_SIZE  # update rect x coordinate
                        self.rect.y = row * TILE_SIZE  # update rect y coordinate
                        self.game.window.blit(self.image, (col * TILE_SIZE, row * TILE_SIZE))

    # This function iterates through the cells inside the matrix level and selects a viable spawn cell for the powerup
    def select_viable_spawn_cell(self, available_powerups):
        # Define a list of all viable cells where powerups can spawn, represented by value 5, ('5'=BRITTLE))
        viable_powerup_cells = [(row, col) for row in range(len(self.game.level.level_matrix)) for col in
                                range(len(self.game.level.level_matrix[row]))
                                if self.game.level.level_matrix[row][col] == 5]

        # Define a list of used cells for every powerup in available_powerups that's not itself and append its location
        used_powerup_cells = [powerup.location for powerup in available_powerups if powerup != self]

        # Check if there are available viable cells for spawning powerups
        if viable_powerup_cells:
            # Choose a random cell among all the valid cells that hasn't been used yet
            chosen_powerup_cell = random.choice(
                [cell for cell in viable_powerup_cells if cell not in used_powerup_cells])

            row, col = chosen_powerup_cell
            self.game.level.level_matrix[row][col] = 9  # assign value 9 ('9'=POWERUP(BR))
            self.location = chosen_powerup_cell  # save the selected cell's location information

            # FOR DEBUGGING /// Uncomment to check if assignment was successful
            # print(f"Assigned PowerUp: {self.image_path} to cell {chosen_powerup_cell}")

            # Return updated powerup location
            return self.location

    # This functions looks at the powerup type (based on its current image_path) and applies its perk
    def apply_perk(self, bomb_explosion_radius, player_bomb_inventory):

        # EXPLOSION RADIUS
        if self.image_path == 'explosion_radius':
            return bomb_explosion_radius + 1, player_bomb_inventory  # increase player bomb explosion radius by 1

        # EXTRA BOMB
        elif self.image_path == 'extra_bomb':
            return bomb_explosion_radius, player_bomb_inventory + 1  # increase player's bomb inventory by 1

        # Return current values if the powerup type doesn't match
        return bomb_explosion_radius, player_bomb_inventory

    # This function handles the removal of the powerup object and the aftermath of it
    def remove_from_game(self):
        # Remove powerup from map and set its row and column location to value 1 ('1'=PATH)
        row, col = self.location
        self.game.level.level_matrix[row][col] = 1
        self.game.powerups.remove(self)
