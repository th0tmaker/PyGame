# Ilijablaster/player.py
import pygame as pg
from settings import TILE_SIZE, IMPASSABLE_CELLS, BG
from bomb import Bomb

vec2d = pg.math.Vector2


class Player:
    def __init__(self, game, name, row_index, column_index, color, move_keys, drop_bomb_key):
        # REFERENCE
        self.game = game  # Reference to Game class to access its attributes & methods

        # DESCRIPTION
        self.name = name  # Player name (for multiplayer purposes, e.g., Player 1, Player 2)

        # LOCATION (INSIDE LEVEL MATRIX)
        self.location = (row_index, column_index)  # Current player location based on row and column indices

        # HITBOX (The definition of a (rect) represents the tangible presence of the object within the program))
        self.rect = pg.Rect(column_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)  # Player rect

        # COLOR
        self.color = color  # Player color

        # MOVEMENT
        self.direction = vec2d(0, 0)  # Initial direction of movement (no direction)
        self.velocity = 2  # Player velocity of movement (adjust to change movement speed)

        # CONTROL KEYS
        self.move_keys = move_keys  # Move Keys: List of keys used for player movement, defined during instantiation
        self.drop_bomb_key = drop_bomb_key  # Drop Bomb Key: Key used to drop bombs, defined during instantiation

        # BOMB INTERACTION
        self.bombs = []  # List to store player's available bombs
        self.bomb_inventory = 1  # Number of bombs in inventory the player can carry
        self.bomb_explosion_radius = 1  # Radius of the player's bomb explosions (passed to Bomb's __init__ method)
        self.dropped_bomb = False  # Flag indicating if the player has dropped a bomb.
        self.hit_by_bomb_explosion = False  # Flag indicating if the player has been hit by a bomb explosion

        # CREEP INTERACTION
        self.checking_for_creep_collision = True  # Flag indicating if game is checking for collision with creep
        self.collided_with_creep = False  # Flag indicating if the player had collided with a creep

        # ICE TILE INTERACTION
        self.on_ice_tile = False  # Flag indicating if the player is currently on an ice tile
        self.ice_tile_direction = None  # Direction of movement affected by the ice tile

        # EXIT PORTAL INTERACTION
        self.exit_portal_animation_start_time = 0  # Timestamp for the start of the exit portal animation
        self.exit_portal_animation_duration = 200  # Duration of exit portal animation in milliseconds
        self.checking_exit_portal_collision = True  # Flag indicating if game is checking for collision with exit portal
        self.start_exit_portal_animation = False  # Flag to indicate whether the exit portal is currently in animation
        self.collided_with_exit_portal = False  # Flag indicating if the player had collided with the exit portal

        # DEATH
        self.death_animation_start_time = 0  # Timestamp for the start of the death animation
        self.death_animation_duration = 105  # Duration of the death animation in milliseconds
        self.start_death_animation = False  # Flag to indicate whether the player's death is currently in animation

        # UPDATE
        self.stop_updating = False

    # This function handles the drawing of the player object and updates dynamically
    def draw(self):
        # Check if the player has collided with the exit portal
        if self.collided_with_exit_portal:
            self.exit_portal_animation()  # run exit portal animation

        # Check if the player has collided with a creep (enemy) or has been hit by any of the bomb's explosions
        elif self.collided_with_creep or self.hit_by_bomb_explosion:
            self.death_animation()  # run death animation

        # If no special animation is triggered, draw the rect that is representing the player normally
        else:
            pg.draw.rect(self.game.window, self.color, self.rect)
            pg.draw.rect(self.game.window, BG, self.rect, 1)  # draw a border (width=1) around the player's rect

    # This function handles the input keys from the user that are connected to controlling the player
    def input_keys(self):
        keys = pg.key.get_pressed()  # retrieve the currently pressed keys

        # // *** MOVEMENT *** //

        # Define movement directions and associate them with corresponding keys
        directions = [vec2d(0, -1), vec2d(0, 1), vec2d(-1, 0), vec2d(1, 0)]

        # Set the player's direction based on the pressed input keys, or keep direction (0, 0) if no key is pressed
        input_direction = next((direction for key, direction in zip(self.move_keys, directions)
                                if keys[key]), vec2d(0, 0))

        # Handle the player movement logic when player is on ice tile
        if not self.on_ice_tile:
            self.direction = input_direction
        else:
            # If player is on ice tile AND standing still (direction is vec2d(0, 0))
            if self.direction == vec2d(0, 0):
                self.direction = input_direction

        # // *** DROP BOMB *** //

        # Check if bomb inventory is greater than 0 and the drop bomb key is pressed, but bomb has not been dropped yet
        if self.bomb_inventory > 0 and keys[self.drop_bomb_key] and not self.dropped_bomb:
            self.drop_bomb()
            self.dropped_bomb = True

        # If the drop bomb key is not pressed
        elif not keys[self.drop_bomb_key]:
            self.dropped_bomb = False

    # This function handles the movement (and movement restriction) logic for the player
    def movement(self):
        next_self_rect = self.rect.copy()  # create a copy of player rect to utilize for movement examination
        next_self_rect.move_ip(self.direction * self.velocity)  # move copy in the desired direction at the set velocity

        # // *** MOVEMENT RESTRICTION *** //

        # Get the row and column indices of the player's current location inside the level matrix
        row, col = self.location
        # Iterate over a 3x3 grid of adjacent tiles centered around the player's tile location
        for d_row in range(-1, 2):  # iterate over rows from -1 to 1 (inclusive)
            for d_col in range(-1, 2):  # iterate over columns from -1 to 1 (inclusive)
                tile_row = row + d_row  # calculate the row index of the adjacent tile
                tile_col = col + d_col  # calculate the column index of the adjacent tile

                # Check if the calculated adjacent tile indices are within the bounds of the level matrix
                if 0 <= tile_row < len(self.game.level.level_matrix) and 0 <= tile_col < len(
                        self.game.level.level_matrix[0]):

                    # Check if the tile at the calculated indices contains an impassable object
                    if self.game.level.level_matrix[tile_row][tile_col] in IMPASSABLE_CELLS:
                        # Create a rect representing the impassable object at the current tile
                        impassable_rect = pg.Rect(tile_col * TILE_SIZE, tile_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                        # Check for collision between the player's next position and the impassable object
                        if next_self_rect.colliderect(impassable_rect):

                            # Calculate the x and y distances between the player and the impassable rect
                            dx = next_self_rect.centerx - impassable_rect.centerx  # horizontal distance
                            dy = next_self_rect.centery - impassable_rect.centery  # vertical distance

                            # Tolerance threshold for enacting the push logic below
                            enactment_tolerance = TILE_SIZE // 4

                            # * CHECK FOR DOMINANT DIRECTION WHEN A COLLISION OCCURS *

                            # If dx is greater than dy (in absolute terms)...
                            # Collision is assumed to have happened on the left or right side of the impassable rect
                            if abs(dx) > abs(dy):
                                if dx > 0:
                                    # If delta x > 0, it means the next_self.rect is further along the x-axis
                                    next_self_rect.left = impassable_rect.right

                                    # FOR DEBUGGING /// Uncomment to check if code was successful
                                    # print("Collision on 'RIGHT' side of impassable tile!")
                                else:
                                    # If delta x < 0, it means the impassable_rect is further along the x-axis
                                    next_self_rect.right = impassable_rect.left

                                    # FOR DEBUGGING /// Uncomment to check if code was successful
                                    # print("Collision on 'LEFT' side of impassable tile!")

                                if abs(next_self_rect.centery - impassable_rect.centery) > enactment_tolerance \
                                        and self.game.level.level_matrix[tile_row][tile_col] == 2:
                                    self.direction = vec2d(0, 1 if
                                                           next_self_rect.centery > impassable_rect.centery else -1)
                                    next_self_rect.move_ip(self.direction * self.velocity)

                            # If dx is NOT greater than dy (in absolute terms)...
                            # Collision is assumed to have happened on the top or bottom side of the impassable rect
                            else:
                                if dy > 0:
                                    # If delta y > 0, it means the next_self.rect is further along the y-axis
                                    next_self_rect.top = impassable_rect.bottom

                                    # FOR DEBUGGING /// Uncomment to check if code was successful
                                    # print("Collision on 'BOTTOM' side of impassable tile!")
                                else:
                                    # If delta y < 0, it means the impassable_rect is further along the y-axis
                                    next_self_rect.bottom = impassable_rect.top

                                    # FOR DEBUGGING /// Uncomment to check if code was successful
                                    # print("Collision on 'TOP' side of impassable tile!")

                                # Apply same logic as in multiline comment above but change direction to LEFT/RIGHT
                                if abs(next_self_rect.centerx - impassable_rect.centerx) > enactment_tolerance \
                                        and self.game.level.level_matrix[tile_row][tile_col] == 2:
                                    self.direction = vec2d(
                                        1 if next_self_rect.centerx > impassable_rect.centerx else -1, 0)
                                    next_self_rect.move_ip(self.direction * self.velocity)

        # Update player location and rect position
        self.location = (next_self_rect.centery // TILE_SIZE, next_self_rect.centerx // TILE_SIZE)
        self.rect = next_self_rect

    # This function handles the collision logic for the player
    def collision(self):
        self.bomb_collision()
        self.explosion_collision()
        self.creep_collision()
        self.ice_tile_collision()
        self.powerup_collision()
        self.exit_portal_collision()

    # This function handles the bomb collision logic
    def bomb_collision(self):
        # Iterate through all players in the game and through each bomb owned by the current player
        for player in self.game.players:
            for bomb in player.bombs:
                bomb_row, bomb_column = bomb.location  # extract bomb row and column indices

                # Check if both player and bomb have valid rects
                if player.rect is not None and bomb.rect is not None:
                    bomb.pushback_player()  # enact the player pushback function

                    # Check if ANY player is colliding with the bomb after pushback
                    any_player_colliding = any(player.rect.colliderect(bomb.rect) for player in self.game.players)

                    # If no player is colliding with the bomb, update the level matrix value to 6 ('6'=BOMB)
                    if not any_player_colliding:
                        self.game.level.level_matrix[bomb_row][bomb_column] = 6

    # This function handles the bomb explosion collision logic
    def explosion_collision(self):
        for player in self.game.players:

            # Skip collision check if player has collided with a creep
            if player.collided_with_creep:
                continue

            # Iterate through every bomb in the player's bomb inventory
            for bomb in player.bombs:
                # If the explosion portion of the bomb object is active
                if bomb.explosion_active:
                    explosion_rects = bomb.explosion()  # retrieve the explosion rects from the bomb
                    for rect in explosion_rects:
                        for target_player in self.game.players:
                            if rect.colliderect(target_player.rect) and not target_player.hit_by_bomb_explosion:
                                # Explosion rect colliding with player aftermath
                                target_player.velocity = 0
                                target_player.hit_by_bomb_explosion = True
                                target_player.start_death_animation = True
                                target_player.death_animation_start_time = pg.time.get_ticks()

                                # Use target player variable to check which player got hit
                                # print(f"{target_player.name} hit by {bomb.player.name}'s bomb blast!")

                                self.game.audio.play_sfx('player_death', volume=0.2)

    # This function handles the creep (enemy) collision logic
    def creep_collision(self):
        for player in self.game.players:

            # Skip creep collision check if player has been hit by bomb explosion
            if player.hit_by_bomb_explosion:
                continue

            # Creep collision criteria
            if player.checking_for_creep_collision:
                creep_collision_criteria = any(
                    (not (creep.transmutation_state and creep.transmutation_state.alert_phase_active)
                     and not creep.is_blinking_before_death
                     and not creep.ignore_player_collision
                     and player.rect.collidepoint((creep.rect.centerx + x_offset, creep.rect.centery + y_offset)))
                    for creep in self.game.creeps
                    for x_offset, y_offset in [(5, 0), (-5, 0), (0, 5), (0, -5)]
                )

                if creep_collision_criteria:
                    player.velocity = 0
                    player.collided_with_creep = True
                    player.checking_for_creep_collision = False
                    player.start_death_animation = True
                    player.death_animation_start_time = pg.time.get_ticks()

                    self.game.audio.play_sfx('player_death', volume=0.2)
                    break

    # This function handles the ice tile collision logic
    def ice_tile_collision(self):
        # Check if the player's rect collides with an ice tile object, if it does, put the colliding ice tile in a list
        colliding_ice_tiles = [ice_tile for ice_tile in self.game.ice_tiles if self.rect.colliderect(ice_tile.rect)]

        # If colliding with at least one ice tile, update player's state
        if colliding_ice_tiles:
            self.on_ice_tile = True
            self.ice_tile_direction = self.direction

            # Calculate next position based on slide velocity
            slide_velocity = max(1, self.velocity // 2)
            next_self_rect = self.rect.move(self.ice_tile_direction * slide_velocity)

            # Get playerlocation then check if the player row and column position is not on any colliding ice tile
            player_row, player_column = self.location
            player_location_not_on_ice = all((player_row != ice_tile.row or player_column != ice_tile.column)
                                             for ice_tile in colliding_ice_tiles)

            # Iterate over a 3x3 grid of adjacent tiles centered around the player's tile location
            for tile_row, tile_col in ((player_row + d_row, player_column + d_col)
                                       for d_row in range(-1, 2)
                                       for d_col in range(-1, 2)):

                # Check if the calculated adjacent tile indices are within the bounds of the level matrix
                if 0 <= tile_row < len(self.game.level.level_matrix) and 0 <= tile_col < len(
                        self.game.level.level_matrix[0]):

                    # Check if the cell at the calculated indices is an impassable cell
                    if self.game.level.level_matrix[tile_row][tile_col] in IMPASSABLE_CELLS:
                        # If True, create an impassable rect from that cell
                        impassable_rect = pg.Rect(tile_col * TILE_SIZE, tile_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                        # Check for collision with impassable rect if player is on ice tile
                        if next_self_rect.colliderect(impassable_rect) and self.on_ice_tile:
                            # Reset direction if colliding with impassable rect
                            self.direction = vec2d(0, 0)
                            self.ice_tile_direction = self.direction
                            break
            else:
                # Update ice tile direction if player's location is not on any ice tile
                if player_location_not_on_ice:
                    self.ice_tile_direction = self.direction
        else:
            # If not colliding with any ice tile, reset player's on ice tile flag state
            self.on_ice_tile = False

    # This function handles the powerup collision logic
    def powerup_collision(self):
        # Iterate through all powerups in the game
        for powerup in self.game.powerups:
            # Check if the player's center point collides with the powerup's rect
            if powerup.rect.collidepoint(self.rect.center):
                # Apply the powerup's effects to the player that has collided with the powerup rect
                self.bomb_explosion_radius, self.bomb_inventory = powerup.apply_perk(
                    self.bomb_explosion_radius, self.bomb_inventory)
                self.game.audio.play_sfx('powerup_pickup', volume=0.2)  # play a sound effect for powerup pickup

                powerup.remove_from_game()  # remove the powerup from the game

        # Return the updated bomb explosion radius and bomb inventory after powerup collision
        return self.bomb_explosion_radius, self.bomb_inventory

    # This function handles the exit portal collision logic
    def exit_portal_collision(self):
        if self.game.exit_portal:
            if self.checking_exit_portal_collision:
                # Calculate the center coordinates of player's rectangle and exit portal's rectangle
                player_center = self.rect.center
                exit_portal_center = self.game.exit_portal.rect.center

                if player_center[0] == exit_portal_center[0] and player_center[1] == exit_portal_center[1] \
                        and not self.game.exit_portal.image_path == 'closed':
                    self.collided_with_exit_portal = True
                    self.checking_exit_portal_collision = False

                    # Start the exit portal animation
                    self.start_exit_portal_animation = True
                    self.exit_portal_animation_start_time = pg.time.get_ticks()
                    self.velocity = 0

            else:
                if not any(player.rect.colliderect(self.game.exit_portal.rect) for player in self.game.players):
                    self.checking_exit_portal_collision = True
                    self.collided_with_exit_portal = False

    # This function handles the bomb dropping logic of the player
    def drop_bomb(self):
        row, col = self.location  # retrieve player's current row and column positions

        # Bomb drop conditions
        bomb_drop_conditions = (
            self.bomb_inventory > 0,
            not any(bomb.location == (row, col) for bomb in self.bombs),
            self.game.level.level_matrix[row][col] not in [7, 8],
            not self.start_death_animation
        )

        # If all conditions are met, create bomb object
        if all(bomb_drop_conditions):
            bomb = Bomb(self.game, self, row, col, self.bomb_explosion_radius)
            self.bombs.append(bomb)  # append bomb to player's bombs list
            self.dropped_bomb = True  # set flag indicating a bomb has been dropped
            self.bomb_inventory -= 1  # reduce the bomb inventory after dropping bombs

            bomb_row, bomb_column = bomb.location
            self.game.level.level_matrix[bomb_row][bomb_column] = 66

    # This function handles how the player regains the bomb after dropping it
    def regain_bomb(self):
        current_time = pg.time.get_ticks()
        regain_delay = 15

        # Use a list comprehension to filter bombs that need to be discarded
        bombs_to_discard = [bomb for bomb in self.bombs if
                            not bomb.is_active and current_time - bomb.overall_start_time >= regain_delay]

        # Remove the discarded bombs and increment the bomb inventory
        for bomb in bombs_to_discard:
            self.bombs.remove(bomb)
            self.bomb_inventory += 1

    # This function handles the player's death animation
    def death_animation(self):
        # Iterate over each player in the game and check if the player's death animation should start
        for player in self.game.players:
            if player.start_death_animation:

                # Determine the number of rows to draw based on elapsed time
                current_time = pg.time.get_ticks()
                elapsed_time = current_time - player.death_animation_start_time
                num_rows = min(player.rect.height // 2, player.rect.width // 2)
                rows_to_draw = min(num_rows, elapsed_time // player.death_animation_duration + 1)

                # Draw the player's rect during the death animation with a border radius
                if rows_to_draw < num_rows:
                    pg.draw.rect(self.game.window, player.color, player.rect, border_radius=30)

                # Draw another rect in background color inside the player during the death animation
                middle_x = player.rect.x + player.rect.width // 2
                middle_y = player.rect.y + player.rect.height // 2
                for i in range(rows_to_draw):
                    rect_size = 2 * i
                    rect_offset = rect_size // 2
                    rect = pg.Rect(middle_x - rect_offset, middle_y - rect_offset, rect_size, rect_size)
                    pg.draw.rect(self.game.window, BG, rect, 1, border_radius=30)

                # Stop the animation when all rows have been drawn
                if rows_to_draw >= num_rows:
                    # Transfer player information to the end game info dict
                    player.game.player_end_info_dict[player.name] = {
                        'color': player.color,
                        'center_coords': player.rect.center,
                        'collided_with_ep': player.collided_with_exit_portal,
                        'collided_with_creep': player.collided_with_creep,
                        'hit_by_bomb_explosion': player.hit_by_bomb_explosion,
                    }

                    # Stop the death animation, remove player, and switch to end game menu screen
                    player.start_death_animation = False
                    self.game.players.remove(player)
                    self.game.menu.switch_to_end()
                    break

    # This function handles the player's exit portal animation
    def exit_portal_animation(self):
        # Iterate over each player in the game and check if the player's exit portal animation should start
        for player in self.game.players:
            if player.start_exit_portal_animation:

                # Calculate the elapsed time since the start of the exit portal animaiton
                current_time = pg.time.get_ticks()
                elapsed_time = current_time - player.exit_portal_animation_start_time

                # Draw the player's rect during the exit portal animation
                pg.draw.rect(self.game.window, player.color, player.rect)

                # Check if enough time has passed for the next animation step
                if elapsed_time >= player.exit_portal_animation_duration:
                    # Reset the animation start time for the next iteration
                    player.exit_portal_animation_start_time = current_time

                    # Shrink the original player rect to create the visual illusion of teleporting
                    player.rect.inflate_ip(-2, -2)

                    # Check if the width or height of the original rectangle is <= 0
                    if player.rect.width <= 0 or player.rect.height <= 0:
                        # Transfer player information to the end game info dict
                        player.game.player_end_info_dict[player.name] = {
                            'color': player.color,
                            'center_coords': player.rect.center,
                            'collided_with_ep': player.collided_with_exit_portal,
                            'collided_with_creep': player.collided_with_creep,
                            'hit_by_bomb_explosion': player.hit_by_bomb_explosion,
                        }

                        # Stop the exit portal animation, remove player, and switch to end game menu screen
                        player.start_exit_portal_animation = False
                        self.game.players.remove(player)
                        self.game.menu.switch_to_end()
                        break

    # This function makes the player immobile and invunerabl when the game is effectively over
    def make_immobile_and_invunerable_at_end_game(self):
        if len(self.game.players) <= 2:
            for player in self.game.players:
                if player.start_death_animation or player.start_exit_portal_animation:
                    self.stop_updating = True

    # This function handles dynamic updates for the player object
    def update(self):
        if not self.stop_updating:
            self.input_keys()
            self.movement()
            self.collision()
            self.regain_bomb()
            self.make_immobile_and_invunerable_at_end_game()
