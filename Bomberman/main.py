# Ilijablaster/main.py
import sys
from settings import *
from creep import *
from level_layout import level_matrix
from level_manager import LevelManager
from audio_manager import AudioManager
from menu import Menu
from player import Player
from powerup import PowerUp
from exit_portal import ExitPortal


class Game:
    def __init__(self):
        # SETTINGS
        pg.init()  # initialize Pygame
        self.window = pg.display.set_mode(WINDOW_SIZE)  # create the game window
        pg.display.set_caption("Ilijablaster | By Ilija ©")  # set the window title
        pg.display.set_icon(pg.image.load(join(BASE_ICON_DIR, 'ibicon.png')))  # set the window icon
        self.clock = pg.time.Clock()  # create a pygame clock to control the frame rate

        # MENU
        self.menu = Menu(self)  # initialize instance of Menu class as the game menu
        self.in_menu = any([self.menu.in_main_menu, self.menu.in_settings, self.menu.in_controls,
                            self.menu.in_custom, self.menu.in_audio])  # tracks if the game is in any of the menus

        # GAME MODES
        self.game_mode_1player = False  # flag used to track if selected game mode is single player
        self.game_mode_2player = False  # flag used to track if selected game mode is for two players

        # INPUT KEYS MAPPING
        self.available_input_keys = self.define_dict_of_available_input_keys()  # maps available input keys

        # AUDIO
        self.audio = AudioManager(self)  # initialize instance of AudioManager class to manage the game's audio

        # LEVEL
        self.level = LevelManager(self, level_matrix)  # instance of LevelManager class to manage the game's level
        self.level_rows = len(self.level.level_matrix)  # stores the number of rows inside the level's matrix
        self.level_cols = len(self.level.level_matrix[0])  # stores the number of columsn inside the level's matrix

        # POWERUP
        self.powerups = []  # create an empty list to store all the powerups in the game

        # PLAYER
        self.players = []  # create an empty list to store all the players in the game
        self.player_end_info_dict = {}  # create empty dict to store the info of each player when the game ends

        # CREEP
        self.creeps = []  # create an empty list to store all the creeps in the game
        self.ice_tiles = []  # create an empty list to store all the ice tile objects in the game

        # EXIT PORTAL
        self.exit_portal = None  # create a placeholder for the exit portal object, initialized as None

        # PAUSE
        self.pause_surface = None  # create a placeholder for the pause window surface, initialized as None
        self.paused_time = 0  # create a variable to tracks the amount of time the game has been paused
        self.paused = False  # flag used to track if the game is paused
        self.resumed = False  # flag used to track if the game has resumed

    # This function is used to initialize a new game
    def new_game(self):
        # Clears game objects lists
        self.players.clear()
        self.creeps.clear()
        self.powerups.clear()
        self.ice_tiles.clear()

        # Clear the dictionary with the end game player information
        self.player_end_info_dict.clear()

        # Reset Ice Tile cluser id counter to zero
        IceTile.current_cluster_id = 0

        # Reset and set up the level
        self.level.reset()
        self.level.setup()

        # Reset exit portal back to None
        self.exit_portal = None

        # Set the end game soundeffects boolean flags back to False
        self.audio.victory_sfx_playing = False
        self.audio.defeat_sfx_playing = False

        # Set up the powerups, players and creeps
        self.powerups_setup()
        self.player_setup()
        self.creeps_setup()

        # Iterate through all existing creeps and reset their timer data
        for creep in self.creeps:
            if creep.image_path == creep_yellow_imgpath or creep_cyan_imgpath:
                creep.spawn_ice_tiles_timers_dict['start_time'] = pg.time.get_ticks()
                creep.yellow_creep_timers_dict['normal_start_time'] = pg.time.get_ticks()

    # This function defines all the available input keys the user can use to play the game
    @staticmethod
    def define_dict_of_available_input_keys():
        input_keys = {}  # create a dictionary to store the input keys

        # Get all the keys
        alphabet_keys = ALPHABET_INPUT_KEYS
        other_keys = [key.upper() for key in OTHER_INPUT_KEYS]

        # Iterate through both groups of keys
        for char in alphabet_keys:
            input_keys[char.upper()] = getattr(pg, f"K_{char}")

        for key in other_keys:
            input_keys[key.upper()] = getattr(pg, f"K_{key}")

        # return the dictioanry containing input keys
        return input_keys

    # This function extracts the input keys currently present in the options of the controls menu section
    def extract_input_keys_from_options(self, control_options):
        keys = [0] * (len(control_options))  # Initialize a list to store extracted input keys

        # Iterate through control options
        for i, option in enumerate(control_options):
            key_str = option.split('<')[-1].split('>')[0].strip()  # discard all but key string from the option

            # Check if the key string is available in the available_input_keys dictionary
            if key_str in self.available_input_keys:
                # If available, assign the corresponding input key to the keys list
                keys[i] = self.available_input_keys[key_str]

        # Return the list of extracted input keys
        return keys

    # This function sets up the powerups
    def powerups_setup(self):
        pu1 = PowerUp(self, 'explosion_radius')  # create instance of 'explosion radius' and store as powerup 1
        pu2 = PowerUp(self, 'extra_bomb')  # create instance of 'extra bomb' and store as powerup 2

        self.powerups.extend([pu1, pu2])  # add the powerups as a list within the powerups list

        # iterate through the powerups and select a viable cell for spawning them
        for powerup in self.powerups:
            powerup.select_viable_spawn_cell(self.powerups)

    # This function sets up the players and their controls
    def player_setup(self):
        # Extract keys for Player 1 and Player 2
        player1_control_keys = self.extract_input_keys_from_options(self.menu.controls_options_p1[1:6])
        player2_control_keys = self.extract_input_keys_from_options(self.menu.controls_options_p2[1:6])

        # Create dictionaries for player keys
        player_control_keys = {
            'Player 1': dict(zip(['up', 'down', 'left', 'right', 'drop_bomb'], player1_control_keys)),
            'Player 2': dict(zip(['up', 'down', 'left', 'right', 'drop_bomb'], player2_control_keys))
        }

        # Create insance of Player 1 and append into players list
        player1 = Player(self, "Player 1", 1, 1, GREEN,
                         [player_control_keys['Player 1'][key] for key in ['up', 'down', 'left', 'right']],
                         player_control_keys['Player 1']['drop_bomb'])
        self.players.append(player1)

        # If 2 Player mode is selected; also create instance of Player 2 and append into players list
        if self.game_mode_2player:
            player2 = Player(self, "Player 2", 11, 27, BLUE,
                             [player_control_keys['Player 2'][key] for key in ['up', 'down', 'left', 'right']],
                             player_control_keys['Player 2']['drop_bomb'])
            self.players.append(player2)

    # This function creates instances of the Creep class based on total creeps in the game
    def create_creeps(self, total_creeps, creep_path, creep_type):
        # Iterate over the specified number of total creeps passed as an arguement
        for i in range(total_creeps):
            # Create a new instance of the Creep class
            creep = Creep(self, self.players, f"{creep_type} {i + 1}", creep_path)
            self.creeps.append(creep)  # append the newly created creep instance to the game's creeps list
            creep.select_viable_spawn_cells()  # select viable cells for the creeps to spawn in

    # This function sets up the creeps
    def creeps_setup(self):
        # Define creep types dictionary with corresponding creep parameters
        creep_types = {
            'Purple Creep': {'i': 2, 'path': creep_purple_imgpath},
            'White Creep': {'i': 3, 'path': creep_white_imgpath},
            'Red Creep': {'i': 4, 'path': creep_red_imgpath},
            'Cyan Creep': {'i': 5, 'path': creep_cyan_imgpath},
            'Yellow Creep': {'i': 6, 'path': creep_yellow_imgpath}}

        creep_counts = {}  # initialize dictionary to store creep counts

        # Check if 'Default' option is present in the custom options menu section
        if 'Default' in self.menu.custom_options[0]:
            creep_counts['Purple Creep'] = 6  # number of purple creeps in default mode
            special_creeps_count = {'White Creep': 0, 'Red Creep': 0, 'Cyan Creep': 0, 'Yellow Creep': 0}
            remaining_special_creeps = 7  # number of other 'special' creeps in default mode

            # While special creeps counter is greater than 0
            while remaining_special_creeps > 0:
                # Randomly select a special creep type out of the list
                special_creep = random.choice(['White Creep', 'Red Creep', 'Cyan Creep', 'Yellow Creep'])

                # If the creep is a white creep, the maximum amount of white creeps in default mode is 2
                if special_creep == 'White Creep' and special_creeps_count['White Creep'] >= 2:
                    continue

                # If the creep are other special type, the maximum amount of these creeps in default mode is 3
                if special_creep in ['Red Creep', 'Cyan Creep',
                                     'Yellow Creep'] and special_creeps_count[special_creep] >= 3:
                    continue

                # Increment the count for the chosen special creep
                special_creeps_count[special_creep] += 1

                # Update the total count
                creep_counts[special_creep] = creep_counts.get(special_creep, 0) + 1
                remaining_special_creeps -= 1

        # Check if 'Custom' option is present in the custom options menu section
        elif 'Custom' in self.menu.custom_options[0]:
            # If it is, iterate through the creep name and their data in creep_types dict
            for creep_name, data in creep_types.items():
                # Get the number inside the '<' '>' arrows
                creep_count_key_str = self.menu.custom_options[data["i"]].split('<')[-1].split('>')[0].strip()
                total_creeps = int(creep_count_key_str)  # convert the numeric string into an int
                creep_counts[creep_name] = total_creeps  # update the creep count with the number of total creeps

        # Iterate through the creep count dictionary and create a creep for each creep present
        for creep_name, count in creep_counts.items():
            self.create_creeps(count, creep_types[creep_name]['path'], creep_name)

    # This function takes each cell inside the level matrix and draws them as tiles on screen at their grid position
    def render_cells_into_level_tiles(self):
        self.window.fill(BG)  # fill the background with the BG color

        # Iterate through each row inside the level matrix
        for row, row_values in enumerate(self.level.level_matrix):
            # Iterate through each column of a row value
            for column, cell_value in enumerate(row_values):
                # Create a tile rect object
                tile_rect = pg.Rect((column * TILE_SIZE, row * TILE_SIZE), (TILE_SIZE, TILE_SIZE))

                if cell_value == 0:  # Border tile
                    self.draw_border_tile(tile_rect)

                elif cell_value in {1, 3, 4}:  # Passable tiles
                    pg.draw.rect(self.window, BG, tile_rect)

                elif cell_value == 2:  # Pillar tile
                    self.draw_pillar_tile(tile_rect)

                elif cell_value in {5, 7, 9}:  # Brittle tiles
                    self.draw_brittle_tile(tile_rect, cell_value)

                elif cell_value == 8:  # Portal tile
                    self.exit_portal = ExitPortal(self, (row, column))

    # This function draws the black border tiles around the edges of the screen
    def draw_border_tile(self, tile_rect):
        pg.draw.rect(self.window, BLACK, tile_rect)
        pg.draw.rect(self.window, GREY, tile_rect, 1)

    # This function draws the gray pillar tiles
    def draw_pillar_tile(self, tile_rect):
        pg.draw.rect(self.window, GREY, tile_rect)
        pg.draw.rect(self.window, BLACK, tile_rect, 2)

    # This function draws the brittle objects (breakable walls) tiles
    def draw_brittle_tile(self, tile_rect, cell_value):
        colors = {5: COFFEE, 7: COFFEE, 9: COFFEE}  # ('5'=REGULAR BRITTLE, '7'=E.PORTAL(BR), '9'=POWERUP(BR))
        color = colors[cell_value]

        pg.draw.rect(self.window, color, tile_rect)
        self.draw_brittle_tile_stripes(tile_rect)
        pg.draw.rect(self.window, BG, tile_rect, 1)

    # This function draws the black stripes for the brittle objects (breakable walls) tiles
    def draw_brittle_tile_stripes(self, tile_rect):
        num_horizontal_stripes = 4
        stripe_height = tile_rect.height // num_horizontal_stripes

        num_vertical_stripes = 3
        stripe_width = tile_rect.width // num_vertical_stripes

        for i in range(1, num_horizontal_stripes):
            y = tile_rect.top + i * stripe_height
            pg.draw.line(self.window, BLACK, (tile_rect.left, y), (tile_rect.right - 1, y), 2)

        for i in range(1, num_vertical_stripes):
            x = tile_rect.left + i * stripe_width
            pg.draw.line(self.window, BLACK, (x, tile_rect.top), (x, tile_rect.bottom - 1), 2)

    # This function handles the logic for drawing the game objects on the game window
    def render_game_objects(self):
        self.render_cells_into_level_tiles()  # render the cells into tiles

        # Create a dictionary that maps the name of the object with its corresponding objects to draw
        game_objects_to_draw = {
            'ice_tiles': self.ice_tiles,
            'exit_portal': [self.exit_portal] if self.exit_portal else [],
            'death_sigils': None,
            'powerups': self.powerups,
            'players': self.players,
            'bombs': [bomb for player in self.players for bomb in player.bombs],
            'yellow_immune_creep': [creep for creep in self.creeps if
                                    creep.image_path == creep_yellow_imgpath and creep.transmutation_active],
            'other_creeps': [creep for creep in self.creeps if
                             not (creep.image_path == creep_yellow_imgpath and creep.transmutation_active)]
        }

        # Iterate through each object type and its corresponding objects to draw
        for obj_type, objects in game_objects_to_draw.items():

            # If object type is 'death sigils', call the death sigils render function
            if obj_type == 'death_sigils':
                self.render_death_sigils()

            # If object type is 'yellow_immune_creep'
            elif obj_type == 'yellow_immune_creep':
                # iterate through all such objects and rraw the object normally
                for obj in objects:
                    obj.draw()
                    # Iterate through every player's bomb object and daw it on top of the yellow immune creep
                    for player in self.players:
                        for bomb in player.bombs:
                            bomb.draw()

            # If object type is 'other_creeps'
            elif obj_type == 'other_creeps':
                # iterate through all such objects and rraw the object normally
                for obj in objects:
                    obj.draw()

            # If object type is 'bombs'
            elif obj_type == 'bombs':
                # iterate through all such objects and rraw the object normally
                for obj in objects:
                    obj.draw()

            # Else draw every other object with players being drawn above them
            else:
                for obj in objects:
                    if obj_type == 'players':
                        obj.draw()
                    else:
                        obj.draw()

    # This function handles the logic for creating and displaying the death sigils when a player dies
    def render_death_sigils(self):
        # Define a dictionary mapping a player color to its corresponding death sigil image of same color
        death_sigils = {
            GREEN: pg.image.load(join(BASE_IMG_DIR, 'death_sigils', 'death_sigil_green.png')).convert_alpha(),
            BLUE: pg.image.load(join(BASE_IMG_DIR, 'death_sigils', 'death_sigil_blue.png')).convert_alpha()
        }

        # Iterate through each player's end information
        for player_name, player_info in self.player_end_info_dict.items():
            player_color = player_info.get('color')
            center_coords = player_info.get('center_coords')
            collided_with_creep = player_info.get('collided_with_creep')
            hit_by_bomb_explosion = player_info.get('hit_by_bomb_explosion')

            # If the player color is valid and the player collided with a creep or was hit by a bomb explosion
            if player_color and (collided_with_creep or hit_by_bomb_explosion):
                death_sigil = death_sigils.get(player_color)  # get the corresponding death sigil image

                # If the death sigil image exists create a rect object around it and display on game window
                if death_sigil:
                    death_sigil_rect = death_sigil.get_rect(center=center_coords)  # obtain coords from end_info_dict
                    self.window.blit(death_sigil, death_sigil_rect)

    # This function creates a new surface and renders it on the game window when the game is paused
    def render_pause_screen(self):
        self.pause_surface = pg.Surface((self.window.get_width(), self.window.get_height()))
        self.pause_surface.fill(DARKBLUE)
        font = pg.font.Font(join(BASE_FONT_DIR, 'pause_screen(kindlyrewind).ttf'), 60)
        text_surface = font.render('GAME PAUSED', True, WHITE)

        # Position the text in the middle
        text_width = self.window.get_width() // 2
        text_height = self.window.get_height() // 2
        text_rect = text_surface.get_rect(center=(text_width, text_height - 20))

        self.pause_surface.blit(text_surface, text_rect)  # display the text surface onto the pause screen surface
        self.window.blit(self.pause_surface, (0, 0))  # display the pause surface onto the game window

    # This function handles the logic for when the game is in paused state
    def pause_game(self):
        self.audio.stop_all_sfx()  # stop any soundeffects that are still playing

        # If not in menu and game not paused
        if not self.in_menu and not self.paused:
            self.paused = True  # set flag used to indicate game is paused to True
            self.resumed = False  # set flag used to indicate game has resumed to False

            # Iterate through all the creeps in the game and handle their timers on pause
            for creep in self.creeps:
                creep.handle_timers_on_pause()

            # Iterate through all the ice tile objects in the game and handle their timers on pause
            for ice_tile in self.ice_tiles:
                ice_tile.handle_timers_on_pause()

            # Iterate through all the players and all the players bombs in the game and handle the bomb timers on pause
            for player in self.players:
                for bomb in player.bombs:
                    bomb.handle_timers_on_pause()

            # Play the pause game soundeffect when this function is called
            self.audio.play_sfx('pause_game', volume=0.2)

    # This function handles the logic for when the game has resumed from the paused state
    def resume_game(self):

        # If game is not paused and not resumed yet
        if self.paused and not self.resumed:
            self.paused = False  # set flag used to indicate game is paused to False
            self.resumed = True  # set flag used to indicate game has resumed to True

            # Iterate through all the creeps in the game and handle their timers on resume
            for creep in self.creeps:
                creep.handle_timers_on_resume()

            # Iterate through all the ice tile objects in the game and handle their timers on resume
            for ice_tile in self.ice_tiles:
                ice_tile.handle_timers_on_resume()

            # Iterate through all the players and their bombs in the game and handle the bomb timers on resume
            for player in self.players:
                for bomb in player.bombs:
                    bomb.handle_timers_on_resume()

    # This function handles the drawing for the entire game and updates dynamically
    def draw(self):
        # If game is in menu, draw the menu
        if self.in_menu:
            self.menu.draw()
        # If game is paused, display the pause screen
        elif self.paused:
            self.render_pause_screen()
        # Every other state, render game objects
        else:
            self.render_game_objects()

        # If game is not in menu but is in end section portion
        if not self.in_menu and self.menu.in_end:
            # Draw the menu again on top
            self.menu.draw()
        # When user exists the end section, reset end surface delay start time to None
        else:
            self.menu.end_surface_delay_start_time = None

    # This function handles the events for the entire game and updates dynamically
    def event_handler(self):
        events = pg.event.get()
        for event in events:

            # When the user clicks the 'X' in the top-right corner of the program's window, exit the program
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # When a key is pressed down
            if event.type == pg.KEYDOWN:
                # If the key is ESCAPE
                if event.key == pg.K_ESCAPE:

                    # If the game is paused, resume the game
                    if self.paused:
                        self.resume_game()

                    # If the user is in menu settings or in a game, switch back to main menu
                    elif self.menu.in_settings or self.game_mode_1player or self.game_mode_2player:
                        self.menu.switch_to_main_menu()

                    # If the user is in the custom, audio or controls section, switch back to settings
                    elif self.menu.in_custom or self.menu.in_audio or self.menu.in_controls:
                        self.menu.switch_to_settings()

                # If the key is 'P'
                if event.key == pg.K_p:
                    # If the game is not paused or the game is not in the end game section
                    if not self.paused and not self.menu.in_end:
                        self.pause_game()  # pause the game
                    else:
                        self.resume_game()  # else, resume the game

            # Handle the specific events for each individual menu section
            if self.menu.in_main_menu:
                self.menu.handle_events(events=events,
                                        rects=self.menu.main_menu_rects,
                                        options=self.menu.main_menu_options)

            elif self.menu.in_settings:
                self.menu.handle_events(events=events,
                                        rects=self.menu.settings_rects,
                                        options=self.menu.settings_options)

            elif self.menu.in_custom:
                self.menu.handle_events(events=events,
                                        rects=self.menu.custom_rects,
                                        options=self.menu.custom_options)

            elif self.menu.in_audio:
                self.menu.handle_events(events=events,
                                        rects=self.menu.audio_rects,
                                        options=self.menu.audio_options)

            elif self.menu.in_controls:
                self.menu.handle_events(events=events,
                                        rects=self.menu.controls_rects,
                                        options=self.menu.controls_options)

            elif self.menu.in_end:
                self.menu.handle_events(events=events,
                                        rects=self.menu.end_rects,
                                        options=self.menu.end_options)

    # This function handles the updating for the entire game and updates dynamically
    def update(self):
        self.menu.update()  # update the menu
        self.audio.update()  # update the audio

        # If the game is not in menu, in pause state or in end game section, keep updating all the game objects
        if not self.in_menu and (not self.paused or self.menu.in_end):

            for player in self.players:
                player.update()

                for bomb in player.bombs:
                    if not player.stop_updating:
                        bomb.update()

            for ice_tile in self.ice_tiles:
                ice_tile.update()

            for creep in self.creeps:
                creep.update()

        pg.display.flip()

    # This function creates a while loop which runs the game continously until the program is terminated
    def run(self):
        while True:
            self.draw()
            self.event_handler()
            self.update()
            self.clock.tick(FPS)
