# Bomberman/bomb.py
import pygame as pg
from settings import TILE_SIZE, BLACK, REDBROWN, RED
from timer_utils import *

vec2d = pg.math.Vector2


class Bomb:
    def __init__(self, game, player, row_index, column_index, explosion_radius):
        # REFERENCE
        self.game = game  # Reference to Game class to access its attributes & methods
        self.player = player  # Reference to Player class to access its attributes & methods

        # POSITION (INSIDE LEVEL MATRIX)
        self.location = (row_index, column_index)  # Current position based on row and column indices

        # HITBOX (The definition of a (rect) represents the tangible presence of the object within the program))
        self.rect = pg.Rect(column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)  # Bomb rect
        self.radius = TILE_SIZE // 2  # Bomb radius (for drawing purposes)

        # COUNTDOWN
        self.countdown_active = True  # The countdown is active when an instance of Bomb object is created
        self.countdown_sound_played = False  # Flag to indicate if the countdown sound has been played

        # EXPLOSION
        self.viable_explosion_directions = [
            (0, 0),  # Represents propagation at bomb's position
            (0, 1),  # Represents UPWARD propagation
            (0, -1),  # Represents DOWNWARD propagation
            (-1, 0),  # Represents LEFTWARD propagation
            (1, 0)]  # Represents RIGHTWARD propagation
        self.explosion_radius = explosion_radius  # Range of the bomb's explosion (referenced inside Player class)
        self.explosion_active = False  # Explosion is not active when an instance of Bomb object is created

        # TIMER DATA
        self.bomb_countdown_timers_dict = {
            # BOMB COUNTDOWN TIMERS
            'current_time': 0,
            'start_time': pg.time.get_ticks(),
            'duration': 3000,
            'time_until_completion': 0,
            'paused_time': 0}
        self.bomb_explosion_timers_dict = {
            # BOMB EXPLOSION TIMERS
            'current_time': 0,
            'start_time': 0,
            'duration': 1000,
            'time_until_completion': 0,
            'paused_time': 0}

        # BOMB OBJECT OVERALL
        self.duration = self.bomb_countdown_timers_dict['duration'] + self.bomb_explosion_timers_dict['duration']
        self.overall_start_time = pg.time.get_ticks() + self.duration  # Define (initial time + duration) start time
        self.is_active = True  # Bomb object is active immediately upon initialization of the class

    # This function handles the drawing of the bomb object and updates dynamically
    def draw(self):
        # DRAW COUNTDOWN ANIMATION
        if self.countdown_active:
            self.countdown_animation()

        # DRAW EXPLOSION ANIMATION
        elif self.explosion_active:
            # Get the row and column indices of the current bomb cell position
            bomb_row, bomb_col = self.location

            # Iterate over each viable explosion direction
            for delta_row, delta_col in self.viable_explosion_directions:
                # Iterate over each distance from the bomb cell position up to the explosion radius
                for distance in range(1, self.explosion_radius + 1):
                    # Calculate the row and column indices of the cell in the current explosion direction and distance
                    row = bomb_row + delta_row * distance
                    col = bomb_col + delta_col * distance

                    # Get the value of the cell from the level matrix
                    cell_value = self.game.level.level_matrix[row][col]

                    # Iterate through every cell (row and col) in the level_matrix
                    if 0 <= row < self.game.level_rows and 0 <= col < self.game.level_cols:

                        # Do not draw explosion circles in following cells:
                        # '0'=BORDER, '2'=PILLAR, '8'=E.PORTAL(AR), '10'=POWERUP(AR)
                        if cell_value in {0, 2, 8, 10}:
                            break

                        # Draw an explosion circle on top of the following cells (but break from drawing elsewhere):
                        # '5'=BRITTLE, '7'=E.PORTAL(BR), '9'=POWERUP(BR)
                        if cell_value in {5, 7, 9}:
                            self.explosion_animation(row, col)
                            break

                        # Draw the rest of the explosion circles where the explosion area rects are located
                        self.explosion_animation(row, col)
                        continue

                    break

    # This function handles pushback physics that occur if a player collides with a bomb that's not that player's bomb
    def pushback_player(self):
        # Ensure bomb has a valid rect, if not, return without running the code below
        if self.rect is None:
            return

        # Iterate through other players and apply pushback collision
        for player in self.game.players:
            if player == self.player:
                continue  # Skip collision check for the player who dropped the bomb

            # If player and bomb are aligned by the center x and y coordinates, return without running the code below
            player_rect = player.rect
            if player_rect.center == self.rect.center:
                return

            # Check for collision between bomb and player
            if not self.rect.colliderect(player_rect):
                continue

            # Calculate the distance between the center of the bomb and the player
            dx = self.rect.centerx - player_rect.centerx
            dy = self.rect.centery - player_rect.centery

            # Determine the closest side of the bomb to the player's center
            if abs(dx) > abs(dy):
                # Closest side is either left or right, push player horizontally away from bomb
                direction_vector = vec2d(1 if dx < 0 else -1, 0)
            else:
                # Closest side is either top or bottom, push player vertically away from bomb
                direction_vector = vec2d(0, 1 if dy < 0 else -1)

            # Gradually move the player in the calculated direction until player is no longer colliding with the bomb
            for _ in range(2):
                player_rect.move_ip(direction_vector)  # move the player's rect in the  direction by one pixel
                if not self.rect.colliderect(player_rect):
                    break  # when bomb and player recta are no longer colliding, exit loop

    # This function handles the animation for the countdown portion of the bomb object
    def countdown_animation(self):
        countdown_color = BLACK
        countdown_timer = self.bomb_countdown_timers_dict['time_until_completion']

        # Cycle through the timer based on countdown 'time until completion'
        if countdown_timer > 2000:
            countdown_color = BLACK

        elif countdown_timer > 1000:
            countdown_color = REDBROWN

            # If the countdown tick sound hasn't been played yet, play it and mark it as played
            if not self.countdown_sound_played:
                self.game.audio.play_sfx('bomb_countdown_tick', volume=0.3)
                self.countdown_sound_played = True

        elif 0 < countdown_timer <= 1000:
            countdown_color = RED

            # If the countdown tick sound has been played, play it again and mark it as not played
            if self.countdown_sound_played:
                self.game.audio.play_sfx('bomb_countdown_tick', volume=0.2)
                self.countdown_sound_played = False

        # Draw the circle that represents the bomb
        pg.draw.circle(self.game.window, countdown_color, (self.rect.centerx, self.rect.centery), self.radius)

    # This function handles the aftermatch for the countdown portion of the bomb object
    def countdown_aftermath(self):
        self.countdown_active = False  # set countdown_active to False
        self.explosion_active = True  # set explosion_active to True (indicating start of explosion portion of the bomb)
        self.bomb_explosion_timers_dict['start_time'] = pg.time.get_ticks()  # init timer as bomb explosion 'start_time'
        self.game.audio.play_sfx('bomb_explosion', volume=0.3)

    # This function sets up the timer for the countdown portion of the bomb object
    def countdown_timer_setup(self):
        # Set up the countdown timer and return a dictionary containing the time until completion
        return {
            'time_until_completion': adjust_bomb_timer(
                start_time=self.bomb_countdown_timers_dict.get('start_time'),
                duration=self.bomb_countdown_timers_dict.get('duration'),
                init_timer=pg.time.get_ticks(),
                on_expire_action=self.countdown_aftermath
            )
        }

    # This function updates the timer for the countdown portion of the bomb object
    def countdown_timer_update(self):
        countdown_timer = self.countdown_timer_setup()
        self.bomb_countdown_timers_dict['time_until_completion'] = countdown_timer['time_until_completion']

    # This function handles the animation for the explosion portion of the bomb object
    def explosion_animation(self, row, col):
        # Define explosion color and size patterns as a dictionary
        EXPLOSION_PATTERN = {
            800: (RED, TILE_SIZE // 3),
            600: (REDBROWN, TILE_SIZE // 4),
            400: (RED, TILE_SIZE // 3),
            200: (REDBROWN, TILE_SIZE // 4),
            0: (RED, TILE_SIZE // 3)
        }

        # Get x and y center coordinates from the row and column of the explosion rects
        y_center = row * TILE_SIZE + TILE_SIZE // 2
        x_center = col * TILE_SIZE + TILE_SIZE // 2

        # Determine the appropriate color and size based on bomb explosion 'time until completion'
        time_until_completion = self.bomb_explosion_timers_dict['time_until_completion']
        for time in sorted(EXPLOSION_PATTERN.keys(), reverse=True):
            if time_until_completion > time:
                color, size = EXPLOSION_PATTERN[time]
                break
        else:
            # If the loop completes without finding a suitable pattern, use default values
            color, size = RED, TILE_SIZE // 3

        # Draw explosion circle
        pg.draw.circle(self.game.window, color, (x_center, y_center), size)

    # This function handles the aftermah for the explosion portion of the bomb object
    def explosion_aftermath(self):
        self.explosion_active = False  # set explosion_active to False
        self.is_active = False  # set bomb self.active flag to False (bomb object no longer active)

    # This function handles the timer setup for the explosion portion of the bomb object
    def explosion_timer_setup(self):
        # Set up the explosion timer and return a dictionary containing the time until completion
        return {
            'time_until_completion': adjust_bomb_timer(
                start_time=self.bomb_explosion_timers_dict.get('start_time'),
                duration=self.bomb_explosion_timers_dict.get('duration'),
                init_timer=pg.time.get_ticks(),
                on_expire_action=self.explosion_aftermath
            )
        }

    # This function handles the explosion logic of the bomb object
    def explosion(self):
        level_matrix = self.game.level.level_matrix  # get the level matrix from the game
        explosion_rects = []  # create a list to store rects representing areas affected by the explosion
        explosion_affected_cells = set()  # create a set to store affected cells by the explosion
        bomb_row, bomb_column = self.location  # get the current bomb position

        # Check if explosion is not active, if so, return an empty list
        if not self.explosion_active:
            return explosion_rects

        # Precompute explosion directions and distances
        explosion_directions = [(delta_row, delta_col) for delta_row, delta_col in self.viable_explosion_directions]
        explosion_max_distance = self.explosion_radius + 1

        # EXPLOSION TIMER SETUP (Get the explosion timer and update the bomb explosion timers dictionary)
        explosion_timer = self.explosion_timer_setup()
        self.bomb_explosion_timers_dict['time_until_completion'] = explosion_timer['time_until_completion']

        # Batch cell value changes
        cell_value_changes = []  # create a list to store cell value changes during the explosion

        # Loop through each direction and distance to compute the explosion
        for delta_row, delta_col in explosion_directions:
            for distance in range(1, explosion_max_distance):
                row = bomb_row + delta_row * distance
                col = bomb_column + delta_col * distance

                # Check if the row or column is out of bounds, if so, exit the loop
                if row < 0 or row >= self.game.level_rows or col < 0 or col >= self.game.level_cols:
                    break  # exit loop if out of bounds

                # Get the cell value at the current position
                cell_value = level_matrix[row][col]

                # Check if the cell value indicates an obstacle, if so, break the loop:
                # '0'=BORDER, '2'=PILLAR, '8'=E.PORTAL(AR), '10'=POWERUP(AR)
                if cell_value in {0, 2, 8, 10}:
                    break

                explosion_affected_cells.add((row, col))  # add cell to the set of affected cells

                # Check if explosion propagation should stop ('5'=BRITTLE, '7'=E.PORTAL(BR), '9'=POWERUP(BR))
                if self.explosion_active and cell_value in {5, 7, 9}:
                    break

                # Update cell value based on explosion impact
                elif cell_value == 5:
                    cell_value_changes.append((row, col, 1))  # change: '5'=BRITTLE -> '1'=PATH
                    break

                elif cell_value == 7:
                    self.game.audio.play_sfx('exit_portal_reveal', volume=0.8)
                    cell_value_changes.append((row, col, 8))  # change: '7'=E.PORTAL(BR) -> '8'=E.PORTAL(AR)
                    break
                elif cell_value == 9:
                    self.game.audio.play_sfx('powerup_reveal', volume=0.8)
                    cell_value_changes.append((row, col, 10))  # change: '9'=POWERUP(BR) -> '10'=POWERUP(AR)
                    break

        # Apply batch cell value changes (old value gets overwritten by new value at specific row & col in level_matrix)
        for row, col, new_value in cell_value_changes:
            level_matrix[row][col] = new_value

        # Create explosion rectangles for affected cells (reuse single Rect object)
        explosion_rect_template = pg.Rect(0, 0, TILE_SIZE // 2, TILE_SIZE // 2)

        # Create explosion rectangles for affected cells
        for row, col in explosion_affected_cells:
            explosion_rect = explosion_rect_template.copy()  # copy to avoid reference issues
            explosion_rect.center = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
            explosion_rects.append(explosion_rect)

        # Enact function that changes/reverts map values for areas affected by bomb
        self.revert_level_matrix_cell_value()

        # Return explosion_rects list
        return explosion_rects

    # This function changes the cell value of the bomb back to '1' ('1'=PATH)
    def revert_level_matrix_cell_value(self):
        level_matrix = self.game.level.level_matrix
        bomb_row, bomb_col = self.location
        current_lvl_matrix_value = level_matrix[bomb_row][bomb_col]

        # If map cell value is not: ('3'=PLAYER POS., '4'=PLAYER ADJACENT POS., '7'=E.PORTAL(AR), '8'=E.PORTAL(BR))
        if current_lvl_matrix_value not in {3, 4, 7, 8}:
            level_matrix[bomb_row][bomb_col] = 1  # change every other map cell value to '1'=PATH

        self.rect = None  # reset bomb self.rect back to None value

    # This function starts a new timer count when the game is paused
    def handle_timers_on_pause(self):
        if self.game.paused:
            self.game.paused_time = pg.time.get_ticks()

    # This function updates the new start time for the bomb timers when the game is resumed
    def handle_timers_on_resume(self):
        if not self.game.paused:
            current_time = pg.time.get_ticks()
            paused_time = self.game.paused_time
            start_time = 'start_time'
            update_start_time(self.bomb_countdown_timers_dict, current_time, paused_time, start_time)
            update_start_time(self.bomb_explosion_timers_dict, current_time, paused_time, start_time)

    # This function handles dynamic updates for the bomb object
    def update(self):
        if self.countdown_active:
            self.countdown_timer_update()
