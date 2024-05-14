# Ilijablaster/creep.py
import random
import pygame as pg
from settings import join, TILE_SIZE, BASE_IMG_DIR, IMPASSABLE_CELLS
from timer_utils import adjust_ice_tile_spawn_timer, adjust_ice_tile_remove_timer, update_start_time, \
    update_timer_data_on_pause, update_timer_data_on_resume

vec2d = pg.math.Vector2


# Creep images (by path reference)
creep_purple_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_purple_default.png')
creep_white_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_white_default.png')
creep_red_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_red_default.png')
creep_red_rage_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_red_rage.png')
creep_cyan_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_cyan_default.png')
creep_yellow_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_yellow_default.png')
creep_yellow_immune_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_yellow_immune.png')
creep_yellow_alert_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_yellow_alert.png')
creep_yellow_tmutated_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_yellow_tmutated.png')
creep_cyan_ice_tile_imgpath = join(BASE_IMG_DIR, 'creeps', 'creep_cyan_ice_tile.png')

# A dictionary that is used as a cache with preloaded and scaled creep images
creep_image_cache = {
    creep_purple_imgpath: pg.transform.smoothscale(pg.image.load(creep_purple_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_white_imgpath: pg.transform.smoothscale(pg.image.load(creep_white_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_red_imgpath: pg.transform.smoothscale(pg.image.load(creep_red_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_red_rage_imgpath: pg.transform.smoothscale(pg.image.load(creep_red_rage_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_cyan_imgpath: pg.transform.smoothscale(pg.image.load(creep_cyan_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_cyan_ice_tile_imgpath: pg.transform.smoothscale(pg.image.load(creep_cyan_ice_tile_imgpath),
                                                          (TILE_SIZE, TILE_SIZE)),
    creep_yellow_imgpath: pg.transform.smoothscale(pg.image.load(creep_yellow_imgpath), (TILE_SIZE, TILE_SIZE)),
    creep_yellow_immune_imgpath: pg.transform.smoothscale(pg.image.load(creep_yellow_immune_imgpath),
                                                          (TILE_SIZE, TILE_SIZE)),
    creep_yellow_alert_imgpath: pg.transform.smoothscale(pg.image.load(creep_yellow_alert_imgpath),
                                                         (TILE_SIZE, TILE_SIZE)),
    creep_yellow_tmutated_imgpath: pg.transform.smoothscale(pg.image.load(creep_yellow_tmutated_imgpath),
                                                            (TILE_SIZE, TILE_SIZE)),
}


class Creep:
    def __init__(self, game, player, description, image_path):
        # REFERENCE
        self.game = game  # Reference to the Game class to access its attributes & methods
        self.player = player  # Reference to the Player class to access its attributes & methods

        # DESCRIPTION
        self.description = description  # Description of the creep type

        # LOCATION (INSIDE LEVEL MATRIX)
        self.location = None  # Current creep location based on row and column indices

        # HITBOX (The definition of a (rect) represents the tangible presence of the object within the program))
        self.rect = None  # Creep rect object

        # IMAGE
        self.image_path = image_path  # Variable that stores the current creep image path
        self.image = None  # Variable that store the current creep display image
        self.load_image()  # Loads creep image from cache inside self.image and makes a rect object from said image

        # MOVEMENT
        self.movement_directions = [
            vec2d(0, 1),  # Up
            vec2d(0, -1),  # Down
            vec2d(-1, 0),  # Left
            vec2d(1, 0),  # Right
        ]
        self.direction = random.choice(self.movement_directions)  # The creep's current direction of movement
        self.velocity = 1  # The creep's default velocity of movement
        self.valid_adjacent_cells = set()  # A set of valid adjacent cells the creep can select to change direction

        # SPAWN MOVEMENT DELAY
        self.on_spawn_delay_duration = 1500  # Before a creep can move it has an on-spawn delay of 1.5 seconds
        self.on_spawn_delay_start_time = pg.time.get_ticks()  # Initialize on-spawn start time
        self.on_spawn_delay_started = False  # Flag indicating if on-spawn delay has been initiated
        self.set_velocity_to_default = True  # Flag to reset the creep's velocity to defaul value if need be

        # BOMB INTERACTION
        self.hit_by_bomb_explosion = False  # Flag used to signal whether the creep was hit by bomb explosion or not

        # RED CREEP ATTRIBUTES
        self.rage_active = False  # Flag used to indicate if red creep is in 'rage' mode
        self.red_creep_velocity_increased_after_hit = False  # Flag for red creep's velocity increase after hit

        # CYAN CREEP ATTIRBUTES
        self.valid_freeze_cells = set()

        # YELLOW CREEP ATTRIBUTES
        self.transmutation_mapping = {}  # Dictionary that maps the yellow creep and its transmutated counterpart creep
        self.transmutation_state = None  # Flag used to indicate if yellow creep is in transmutation state
        self.has_yellow_creep_transmutated = None  # Flag used to indicate whether yellow creep has already transmutated
        self.transmutation_active = False  # Flag used to indicate if transmutation phase is active
        self.alert_phase_active = False  # Flag used to indicate if alert phase is active
        self.normal_phase_time_over = None  # Flag used to indicate if yellow creep's normal phase timer is over
        self.transmutation_phase_time_over = None  # Flag used to indicate if yellow creep's transmutation phase is over

        # COLLISION
        self.ignore_explosion_collision = False  # Flag used to signal if creep should ignore collision w/ explosion
        self.ignore_player_collision = False  # Flag used to signal if creep should ignore collision with player

        # DEATH
        self.is_blinking_before_death = False  # Flag used to signal creep is in blinking state (before it dies)

        # TIMER DATA
        # Death timer data
        self.death_timers_dict = {
            'start_time': 0,
            'current_time': 0,
            'time_until_completion': 0,
            'blink_duration': 1000,
            'rage_duration': 6000}
        # Ice spawning timer data
        self.spawn_ice_tiles_timers_dict = {
            'start_time': 0,
            'duration': 4000}
        # Yellow creep transmutation timer data
        self.yellow_creep_timers_dict = {
            'normal_start_time': 0,
            'transmutation_start_time': 0,
            'normal_duration': random.choice([7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000]),
            'transmutation_duration': random.choice([8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000])}

    # This function loads the image path of the creep object to create an image and defines a rect hitbox for it
    def load_image(self):
        self.image = creep_image_cache.get(self.image_path).convert_alpha()
        self.rect = self.image.get_rect()

    # This function handles the drawing of the creep object and updates dynamically
    def draw(self):
        self.game.window.blit(self.image, self.rect)

    # This function defines a short delay at the start of the game before the enemy creeps are allowed to move
    def enact_short_movement_delay_at_spawn(self):
        # Create a shor delay at the start of the round before the creeps can move by changing their velocity attribute

        current_time = pg.time.get_ticks()
        # Check if the instance of Creep class attribute 'initial_spawn_delay' has not been applied yet
        if not hasattr(self, 'initial_spawn_delay') or not self.on_spawn_delay_started:
            if current_time - self.on_spawn_delay_start_time < self.on_spawn_delay_duration:
                for creep in self.game.creeps:
                    creep.velocity = 0
            else:
                self.on_spawn_delay_started = True

        # Check if the initial spawn delay has already been applied
        if self.on_spawn_delay_started:
            for creep in self.game.creeps:
                # Check if 'set_velocity_to_default' boolean flag is set to True
                if getattr(creep, 'set_velocity_to_default', True):
                    creep.velocity = 1
                else:
                    if creep.red_creep_velocity_increased_after_hit:
                        creep.velocity = 2

    # This function iterates through the cells inside the matrix level and selects a viable spawn cell for the creep
    def select_viable_spawn_cells(self):
        # Create a list that will store any cell that already has a creep at its location
        used_creep_cells = []

        # Create a list of all possible cells where creeps can spawn (represented by value '1', aka path tile)
        possible_creep_cells = [(row_index, col_index) for row_index, row in enumerate(self.game.level.level_matrix) for
                                col_index, value in enumerate(row) if value == 1]

        # If cell is a possible creep cell and not an already used cell, it becomes a valid cell to spawn creeps
        valid_creep_cells = [cell for cell in possible_creep_cells if cell not in used_creep_cells]

        # If there are valid cells to spawn creeps:
        if valid_creep_cells:
            chosen_creep_cell = random.choice(valid_creep_cells)  # choose a random cell among all the valid cells

            # Extract row and column indices of the chosen cell
            row, col = chosen_creep_cell

            # Save the chosen cell location as the creep's location
            self.location = chosen_creep_cell

            # Update the creep's rect position based on its newly assigned location
            self.rect.x = col * TILE_SIZE
            self.rect.y = row * TILE_SIZE

            # Append the chosen cell into used creep cells
            used_creep_cells.append(chosen_creep_cell)

            # Remove the chosen cell from the list of possible creep cells
            possible_creep_cells.remove(chosen_creep_cell)

    # This function includes the pathfinding algorithm and general movement logic for the creep
    def pathfind(self):
        # Create a rectangle representing the next position of the creep
        next_self_rect = self.rect.copy()  # create a copy of creep rect to utilize for movement examination
        next_self_rect.move_ip(self.direction * self.velocity)  # move copy in the desired direction at the set velocity

        # // * PART 1: COLLISION-BASED DIRECTION CHANGE ALGORITHM * //

        available_directions = []  # create a list to store available directions for movement
        opposite_direction = [-self.direction[0], -self.direction[1]]  # store opposite direction of current movement

        collision_detected = False  # define a flag to track whether collision is detected

        level_matrix = self.game.level.level_matrix  # get the matrix representing the game level

        # Calculate what range of rows and columns to examine for collision detection
        min_row = max(0, next_self_rect.top // TILE_SIZE)
        max_row = min(len(level_matrix), (next_self_rect.bottom - 1) // TILE_SIZE + 1)
        min_col = max(0, next_self_rect.left // TILE_SIZE)
        max_col = min(len(level_matrix[0]), (next_self_rect.right - 1) // TILE_SIZE + 1)

        # Iterate through the range of rows and columns to check for collision with cells creeps can NOT pass through
        for row in range(min_row, max_row):
            for col in range(min_col, max_col):

                # Check if the current cell contains an impassable value that the creep cannot pass through
                if level_matrix[row][col] in IMPASSABLE_CELLS and \
                        (level_matrix[row][col] not in {5, 7, 9}  # <-- make exception for these values for white creep
                         or self.image_path != creep_white_imgpath):

                    # Create a rectangle representing the impassable cell
                    impassable_rect = pg.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    # Check if the next position rectangle collides with an impassable rect
                    if next_self_rect.colliderect(impassable_rect):
                        collision_detected = True  # set collision flag to True if collision is detected

                        # Calculate the direction vector towards the impassable cell
                        impassable_direction = [col - self.rect.centerx // TILE_SIZE,
                                                row - self.rect.centery // TILE_SIZE]

                        # Calculate available directions for movement excluding opposite and impassable directions
                        available_directions = [direction for direction in self.movement_directions if
                                                direction != opposite_direction and direction != impassable_direction]

                        break  # no need to continue checking other impassable cells since collision is detected

            if collision_detected:
                break  # No need to continue checking other rows if collision is detected

        # Change direction based on collision
        if collision_detected and available_directions:
            self.direction = random.choice(available_directions)

        # // * PART 2: NON-COLLISION DIRECTION CHANGE BASED ALGORTIHM * //

        # If no collision occurred between the creep's next position and an impassable object
        else:
            self.rect = next_self_rect  # update the creep's position to the next position

            # Call function that toggles the normal and transmutation state of yellow creep
            for creep in self.game.creeps:
                if creep.image_path == creep_yellow_imgpath:
                    creep.toggle_yellow_creep_state(creep)

            # Calculate the center coordinates of the next cell the creep is moving towards
            next_cell_centerx = int(next_self_rect.centerx // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
            next_cell_centery = int(next_self_rect.centery // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2

            # Check if the creep's next position is aligned with the center of the next cell
            aligned_at_centerx = next_self_rect.centerx == next_cell_centerx  # equal in their x coordinate
            aligned_at_centery = next_self_rect.centery == next_cell_centery  # equal in ther y coordinate

            # If the creep's next position is aligned with the center of the next cell, execute the code below
            if aligned_at_centerx and aligned_at_centery:

                # Update the creep's location to represent its current position inside the level matrix (row, column)
                self.location = (int(next_self_rect.y // TILE_SIZE), int(next_self_rect.x // TILE_SIZE))

                # Define a list of offset vectors (directions) to find valid adjacent cells
                offset_vectors = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # from first to last: LEFT, RIGHT, UP, DOWN

                # Get the opposite direction of the creep's current pathing direction
                opposite_direction = self.movement_directions[
                    (self.movement_directions.index(self.direction) + 2) % len(self.movement_directions)]

                # Create a list to store valid adjacent cells based on offset vectors from the creep's current location
                # Each value in the list is a tuple representing the row and column indices of valid adjacent cells
                # For a cell to be valid, it must be within the level boundaries and not be an impassable cell
                self.valid_adjacent_cells = [

                    (self.location[0] + vec[0], self.location[1] + vec[1])  # calculate row and column indices
                    for vec in offset_vectors  # iterate over offset vectors

                    # Check if the calculated row and colimn indices are within the level boundaries
                    if (0 <= self.location[0] + vec[0] < len(level_matrix)) and
                       (0 <= self.location[1] + vec[1] < len(level_matrix[0])) and

                    # Check if the cell at the calculated indices does not contain an impassable value
                       (level_matrix[self.location[0] + vec[0]][
                            self.location[1] + vec[1]] not in IMPASSABLE_CELLS) and

                    # Ensure the cell is not opposite to the current direction
                       (self.location[0] + vec[0], self.location[1] + vec[1]) !=
                       (self.location[0] + opposite_direction[0], self.location[1] + opposite_direction[1])
                ]

                # Create a dictionary to store new directions for adjacent cells
                # The dictionary assigns direction vectors required to move towards each specific valid adjacent cell
                new_directions_for_adjacent_cells = {}

                # Iterate over valid adjacent cells to calculate direction vectors
                for cell in self.valid_adjacent_cells:
                    row, col = cell
                    delta_row = row - self.location[0]
                    delta_col = col - self.location[1]

                    # If difference in rows is 0 and the abs difference in cols is 1, the cell is horizontally adjacent
                    if delta_row == 0 and abs(delta_col) == 1:
                        new_directions_for_adjacent_cells[cell] = vec2d(delta_col, 0)

                    # If difference in cols is 0 and the abs difference in rows is 1, the cell is vertically adjacent
                    elif delta_col == 0 and abs(delta_row) == 1:
                        new_directions_for_adjacent_cells[cell] = vec2d(0, delta_row)

                # FOR DEBUGGING /// Uncomment to check if assignment was successful
                # print("Opposite direction:", opposite_direction)
                # print("Valid Adjacent cells:", valid_adjacent_cells)

                # Iterate over each valid adjacent cell and its corresponding valid direction
                for cell, valid_dir in new_directions_for_adjacent_cells.items():

                    # Determine if and how the direction will be changed
                    if valid_dir == self.direction:
                        if random.random() < 0.5:
                            self.direction = self.direction  # 50% to continue straight
                    else:
                        if random.random() < 0.33:
                            self.direction = valid_dir  # 33% to choose every other valid direction

                    # Check if the current creep's image path matches the cyan creep image path
                    if self.image_path == creep_cyan_imgpath:
                        # Define the current cell to freeze by converting the creep's location to integers
                        current_cell_to_freeze = (int(self.location[0]), int(self.location[1]))

                        # Update the set of valid freeze cells in the game with the valid adjacent cells of the creep
                        self.valid_freeze_cells = set(self.valid_adjacent_cells)
                        self.valid_freeze_cells.add(current_cell_to_freeze)  # include the current cell

    # This function handles the collision logic for the creep
    def collision(self):
        for player in self.game.players:
            for bomb in player.bombs:
                self.bomb_collision(bomb)

        self.explosion_collision()

    # This function handles the bomb collision logic
    def bomb_collision(self, bomb):
        # Check if the bomb is active and its rect attribute exists
        if bomb.is_active and bomb.rect is not None:
            # Check for collision between the creep's rect and the bomb's rect
            if self.rect.colliderect(bomb.rect):
                creep_rect = self.rect.copy()  # store the current position of the creep's rect by making a copy

                # Calculate the distance between the center of the creep's rect and the center of the bomb's rect
                diff_x = self.rect.centerx - bomb.rect.centerx
                diff_y = self.rect.centery - bomb.rect.centery

                # If the difference in distance is greater along the x-axis
                if abs(diff_x) > abs(diff_y):
                    new_x = self.rect.x - (1 if diff_x < 0 else -1) * 1  # move the creep along the X-axis
                    new_y = self.rect.y  # Keep the creep's y-coordinate unchanged
                else:
                    new_x = self.rect.x  # Keep the creep's x-coordinate unchanged
                    new_y = self.rect.y - (1 if diff_y < 0 else -1) * 1  # move the creep along the Y-axis

                # If the creep's position has changed
                if not new_x == self.rect.x or not new_y == self.rect.y:
                    # Define new movement directions for the creep and randomly shuffle the new directions list
                    new_directions = [vec2d(0, -1), vec2d(0, 1), vec2d(-1, 0), vec2d(1, 0)]
                    random.shuffle(new_directions)

                    # Assign the first direction from the shuffled list as the new direction for the creep
                    self.direction = new_directions[0]

                # Update the creep's rect 'x' and 'y' coordinates
                creep_rect.topleft = (new_x, new_y)
                self.rect = creep_rect

    # This function handles the explosion collision logic
    def explosion_collision(self):
        # Collect the center points of explosion area rects from active bombs
        explosion_centers = set()
        for player in self.game.players:
            for bomb in player.bombs:
                if bomb.explosion_active:
                    # Update the set with the center points of explosion areas from active bombs
                    explosion_centers.update(rect.center for rect in bomb.explosion())

        # Iterate over creeps and check for collision with explosion centers
        for creep in self.game.creeps:
            # Skip creeps already hit by bomb explosion or yellow creeps with transmutation active
            if (creep.hit_by_bomb_explosion or (creep.image_path == creep_yellow_imgpath and creep.transmutation_active)
                    or creep.ignore_explosion_collision):
                continue

            # Check for collision with explosion centers
            for center in explosion_centers:
                if creep.rect.collidepoint(center):
                    # Set creep's flag 'hit by bomb explosion' as True and start its death timer
                    creep.hit_by_bomb_explosion = True

                    # Start death timer based on creep type (red creep death timer starts after rage duration expires)
                    creep.death_timers_dict['start_time'] = pg.time.get_ticks() + (
                        creep.death_timers_dict['rage_duration'] if creep.image_path == creep_red_imgpath
                        else creep.death_timers_dict['blink_duration']
                    )
                    break  # No need to check further explosion centers for this creep

        # // * HANDLE DEATH ANIMATION AFTER CREEP IS HIT BY BOMB EXPLOSION * //
        for creep in self.game.creeps:
            if creep.hit_by_bomb_explosion:
                creep.death(creep)

    # This function handles the death logic for the creep
    def death(self, creep):
        # Update the death timer current time and calculate the remaining time until completion
        self.death_timers_dict['current_time'] = pg.time.get_ticks()
        self.death_timers_dict['time_until_completion'] = creep.death_timers_dict[
                                                              'start_time'] - self.death_timers_dict[
                                                              'current_time']

        time_until_complete = self.death_timers_dict['time_until_completion']

        # Create a blank image to simulate a blink effect during the death animation
        blank_image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)  # create blank surface with alpha channel
        blank_image.fill((0, 0, 0, 0))  # fill with fully transparent color

        # Retrieve the creep's image from the cache
        creep_image = creep_image_cache.get(creep.image_path)

        # Check if the remaining time until completion of the creep's death animation falls within the range
        # where the creep should exhibit a specific behavior, such as blinking or entering a rage state
        if creep_image:
            if self.death_timers_dict['blink_duration'] < time_until_complete <= self.death_timers_dict[
                    'rage_duration']:

                # If creep in rage state, adjust velocity and change image if creep is centered by its x and y coords
                creep_current_row, creep_current_col = creep.location
                creep_next_row, creep_next_col = int(creep_current_row + creep.direction[0]), int(
                    creep_current_col + creep.direction[1])
                creep_current_center_x = creep_current_col * TILE_SIZE + TILE_SIZE // 2
                creep_current_center_y = creep_current_row * TILE_SIZE + TILE_SIZE // 2
                creep_next_center_x = creep_next_col * TILE_SIZE + TILE_SIZE // 2
                creep_next_center_y = creep_next_row * TILE_SIZE + TILE_SIZE // 2

                if (creep.rect.centerx == creep_current_center_x and creep.rect.centery == creep_current_center_y) or \
                        (creep.rect.centerx == creep_next_center_x and creep.rect.centery == creep_next_center_y) and \
                        not creep.red_creep_velocity_increased_after_hit:
                    # Increase red creep velocity after hit when rage state is initialized
                    creep.set_velocity_to_default = False
                    creep.red_creep_velocity_increased_after_hit = True

                # Retrieve red creep rage state image from creep image cache
                creep.image = creep_image_cache[creep_red_rage_imgpath]

            else:
                # If not in rage state, set normal death parameters
                creep.velocity = 0
                creep.set_velocity_to_default = False
                creep.red_creep_velocity_increased_after_hit = False
                creep.is_blinking_before_death = True

                # Toggle between normal and blank images to create the blinking effect
                if 800 < time_until_complete <= 1000 or 400 < time_until_complete \
                        <= 600 or 0 < time_until_complete <= 200:
                    creep.image = creep_image_cache.get(creep.image_path)
                else:
                    creep.image = blank_image

                # If the time until death animation completion is zero or less, remove the creep
                if time_until_complete <= 0:
                    self.game.creeps.remove(creep)

    # This function iterates through the game's valid freeze cells and creates an ice tile object at that cell
    def create_ice_tiles(self):
        for cell in self.valid_freeze_cells:
            if cell not in IMPASSABLE_CELLS:
                ice_tile = IceTile(self.game, cell, IceTile.current_cluster_id)
                self.game.ice_tiles.append(ice_tile)

        IceTile.current_cluster_id += 1  # increment the latest cluster ID after creating ice tiles

    # This function handles the ice tile timer logic then executes the create_ice_tiles() function after timer expires
    def ice_tiles_timer_setup(self):
        return {
            'start_time': adjust_ice_tile_spawn_timer(
                start_time=self.spawn_ice_tiles_timers_dict['start_time'],
                duration=self.spawn_ice_tiles_timers_dict['duration'],
                init_timer=pg.time.get_ticks(),
                on_expire_action=self.create_ice_tiles
            )
        }

    # This function creates a new creep that represents the transmutated state of a yellow creep
    def create_transmutation_creep(self, creep):
        # Check for signal flag if yellow creep has transmutated
        if creep.has_yellow_creep_transmutated:

            # Collect existing locations of creeps and players to avoid overlapping spawn points with the mutated creep
            creep_locations = {(c.location[0], c.location[1]) for c in self.game.creeps}
            player_locations = {(player.location[0], player.location[1]) for player in self.game.players}

            # Determine viable cells for spawning the transmutation creep.
            viable_transmutation_cells = [
                (row, col)
                for row in range(self.game.level_rows)
                for col in range(self.game.level_cols)
                if (
                        self.game.level.level_matrix[row][col] in [1, 3, 4] and
                        (row, col) not in creep_locations and  # cell not occupied by creep
                        (row, col) not in player_locations  # cell not occupied by player
                )
            ]

            # Randomly select a one of the viable transmutation cell and create a new instance of the Creep class
            if viable_transmutation_cells:
                transmutation_cell = random.choice(viable_transmutation_cells)

                # Transmutated Yellow Creep instance
                transmutation_creep = Creep(
                    self.game,
                    self.player,
                    f"Transmutated Yellow Creep",
                    creep_yellow_alert_imgpath
                )

                transmutation_creep.location = transmutation_cell  # set creep location to transmutation_cell
                transmutation_creep.rect.x = transmutation_cell[1] * TILE_SIZE  # align creep 'x' coord into tile
                transmutation_creep.rect.y = transmutation_cell[0] * TILE_SIZE  # align creep 'y' coord into tile

                # Set which creep is transmuting the created transmuted creep by referencing the creep
                transmutation_creep.transmutation_state = creep

                # Add the transmutated creep to the mapping together with its associated yellow creep
                if creep in self.transmutation_mapping:
                    self.transmutation_mapping[creep].append(transmutation_creep)
                else:
                    self.transmutation_mapping[creep] = [transmutation_creep]

                # Append the transmutation creep into game creeps list
                self.game.creeps.append(transmutation_creep)

            # Reset the flag indicating that the yellow creep has transmuted
            creep.has_yellow_creep_transmutated = False

    # This function removes the new creep that represents the transmutated state of a yellow creep
    def remove_transmutation_creep(self, creep):
        # If creep entry is found inside transmutation mapping dictionary
        if creep in self.transmutation_mapping:
            transmutatation_creep_list = self.transmutation_mapping[creep]

            # Remove the transmutatation creep
            for transmutation_creep in transmutatation_creep_list:
                if transmutation_creep in self.game.creeps:
                    self.game.creeps.remove(transmutation_creep)

            # Also remove the transmutation creep entry from the mapping by referencing its key pair
            del self.transmutation_mapping[creep]

    # This function toggles between the normal and the transmutated state of a yellow creep
    def toggle_yellow_creep_state(self, creep):

        # Do not run code below if creep was hit by bomb explosion
        if creep.hit_by_bomb_explosion:
            return

        # Get the current time and yellow creep timers inside __init__ method dict
        current_time = pg.time.get_ticks()
        timers = creep.yellow_creep_timers_dict

        # Calculate the remaining time for the normal and transmutation phases
        normal_time = timers['normal_start_time'] + timers['normal_duration'] - current_time
        transmutated_time = max(0, timers['transmutation_start_time'] - current_time)

        # If the creep is not currently in the transmutation phase
        if not creep.transmutation_active:
            creep.normal_phase_time_over = False

            # Check if the normal phase time has elapsed
            if normal_time <= 0 and not creep.normal_phase_time_over:
                # Switch to the transmutation phase
                creep.transmutation_active = True
                creep.has_yellow_creep_transmutated = True
                creep.image = creep_image_cache[creep_yellow_immune_imgpath]
                timers['transmutation_start_time'] = current_time + timers['transmutation_duration']

                # Create a transmutation creep
                self.create_transmutation_creep(creep)

                # Mark normal phase is over
                creep.normal_phase_time_over = True

        else:
            creep.transmutation_phase_time_over = False

            # Calculate the center coordinates of the tile where the creep is located
            tile_center_x = (creep.location[1] * TILE_SIZE) + (TILE_SIZE // 2)
            tile_center_y = (creep.location[0] * TILE_SIZE) + (TILE_SIZE // 2)

            # Check if the creep is at the center of its current tile
            if creep.rect.centerx == tile_center_x and creep.rect.centery == tile_center_y \
                    and not creep.transmutation_phase_time_over:
                creep.set_velocity_to_default = False

            # Set alert duration for transmutation creep to alert player before the creep becomes tangible
            alert_phase_duration = 2500

            # Determine the upper bound of time when the alert should be active
            upper_alert_time_bound = timers['transmutation_duration'] - alert_phase_duration

            # Iterate through the mapping of yellow creeps and their transmutation creeps
            for yellow_creep, transmutation_creeps in self.transmutation_mapping.items():
                for tr_creep in transmutation_creeps:
                    # Check if the alert should be active based on the current transmutation time
                    alert_phase_active_condition = upper_alert_time_bound < transmutated_time < timers[
                        'transmutation_duration'] and not yellow_creep.transmutation_phase_time_over

                    # Set the image of the transmutation creep accordingly
                    tr_creep.image = creep_image_cache[
                        creep_yellow_alert_imgpath] if alert_phase_active_condition else creep_image_cache[
                        creep_yellow_tmutated_imgpath]

                    # Set yellow creep flag indicating its alert condition is active as True
                    yellow_creep.alert_phase_active = alert_phase_active_condition

                    # Set transmutation creep ignore player and explosion collision flag as True
                    tr_creep.ignore_explosion_collision = alert_phase_active_condition
                    tr_creep.ignore_player_collision = alert_phase_active_condition

                    # Set the velocity for the transmutation creep based on the alert condition
                    tr_creep.set_velocity_to_default = not alert_phase_active_condition

            if transmutated_time <= 0 and not creep.transmutation_phase_time_over:
                self.remove_transmutation_creep(creep)  # remove the transmutation creep
                creep.transmutation_active = False  # reset the transmutation state for the yellow creep
                creep.set_velocity_to_default = True  # set the velocity back to default
                creep.image = creep_image_cache[creep_yellow_imgpath]  # reset image to the default yellow creep image
                timers['normal_start_time'] = current_time  # reset the start time for the normal phase

                # Mark the transmutation phase as over
                creep.transmutation_phase_time_over = True

    # This function manages the spawn timer for the ice tiles
    def manage_ice_tiles_spawn_timer(self):
        # Set up timer and record the start time of the ice tiles spawn timer
        ice_tiles_spawn_timer = self.ice_tiles_timer_setup()
        self.spawn_ice_tiles_timers_dict['start_time'] = ice_tiles_spawn_timer['start_time']

    # This function starts a new timer count when the game is paused
    def handle_timers_on_pause(self):
        # Record the time at which the game was paused
        if self.game.paused:
            self.game.paused_time = pg.time.get_ticks()

    # This function updates the new start time for the bomb timers when the game is resumed
    def handle_timers_on_resume(self):
        if not self.game.paused:
            current_time = pg.time.get_ticks()
            paused_time = self.game.paused_time

            # Update start times of various timers based on the time elapsed during pause
            update_start_time(self.spawn_ice_tiles_timers_dict, current_time, paused_time, 'start_time')
            update_start_time(self.death_timers_dict, current_time, paused_time, 'start_time')
            update_start_time(self.yellow_creep_timers_dict, current_time, paused_time, 'normal_start_time')
            update_start_time(self.yellow_creep_timers_dict, current_time, paused_time, 'transmutation_start_time')

    def update(self):
        if not self.game.in_menu:
            self.enact_short_movement_delay_at_spawn()
            self.pathfind()
            self.collision()
            self.manage_ice_tiles_spawn_timer()


class IceTile:
    remove_cluster_timers = {}  # Dictionary to store timers for removing ice clusters
    current_cluster_id = 0  # Variable to keep track of the current cluster ID

    def __init__(self, game, cell, cluster_id):
        self.game = game  # Reference to the Game class to access its attributes & methods
        self.row, self.column = cell  # Row and column indices of the ice tile cell
        self.image_path = creep_cyan_ice_tile_imgpath  # Path to the image file for the ice tile
        self.image = None  # Variable that stores the current ice tile image path
        self.rect = None  # Ice tile rect object
        self.cluster_id = cluster_id  # Unique identifier for the ice cluster to which this tile belongs

        # Initialize timer data for the current cluster ID if it's not already in the dictionary
        if cluster_id not in IceTile.remove_cluster_timers:
            IceTile.remove_cluster_timers[cluster_id] = {
                'start_time': 0,
                'remaining_time_at_pause': 0,
                'new_start_time': 0,
                'duration': 15000,
                'new_duration': None}

        # Retrieve timer data for the current cluster ID
        self.remove_cluster_timer_data = IceTile.remove_cluster_timers[self.cluster_id]
        # Record the start time of the removal process for this ice tile
        self.remove_cluster_timer_data['start_time'] = pg.time.get_ticks()

        self.load_image()  # Loads ice tile image from cache inside self.image and makes a rect object from said image
        self.position(cell)  # Defines the ice tile position inside the level matrix

    # This function loads the ice tile image from cache inside the self.image variable and makes a rect object from it
    def load_image(self):
        self.image = creep_image_cache[creep_cyan_ice_tile_imgpath].convert_alpha()
        self.rect = self.image.get_rect()

    # This function sets the position of the ice tile inside the level matrix
    def position(self, cell):
        self.rect.topleft = (cell[1] * TILE_SIZE, cell[0] * TILE_SIZE)

    # This function draws the ice tile image on the game's display window
    def draw(self):
        self.game.window.blit(self.image, self.rect)

    # This function removes a set cluster of ice tiles (based on their id) from the game's ice tile list
    def remove_cluster(self):
        self.game.ice_tiles = [ice_tile for ice_tile in self.game.ice_tiles if
                               ice_tile.cluster_id != self.cluster_id]

    # This function tracks elapsed time and cotrasts it with the duration of the ice tile then executes an action
    def manage_timers(self):
        adjust_ice_tile_remove_timer(timers_dict=self.remove_cluster_timer_data,
                                     init_timer=pg.time.get_ticks(),
                                     duration=self.remove_cluster_timer_data.get('duration'),
                                     start_time=self.remove_cluster_timer_data.get('start_time'),
                                     new_duration=self.remove_cluster_timer_data.get('new_duration'),
                                     new_start_time=self.remove_cluster_timer_data.get('new_start_time'),
                                     on_expire_action=self.remove_cluster)

    # This function saves the remaining time at pause and sets it as the new duration for the ice tile
    def handle_timers_on_pause(self):
        update_timer_data_on_pause(timers_dict=self.remove_cluster_timer_data,
                                   paused=self.game.paused)

    # This function sets a new start time for the ice tile spawn timer when the game is resumed
    def handle_timers_on_resume(self):
        update_timer_data_on_resume(timers_dict=self.remove_cluster_timer_data,
                                    init_timer=pg.time.get_ticks(),
                                    resumed=self.game.resumed)

    # This function handles dynamic updates for the ice tile object
    def update(self):
        self.manage_timers()
