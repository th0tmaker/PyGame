# Ilijablaster/menu.py
import sys
import pygame as pg
from settings import join, BASE_IMG_DIR, BASE_FONT_DIR, ALPHABET_INPUT_KEYS, OTHER_INPUT_KEYS, BLACK, WHITE, GREEN, BLUE


class Menu:
    def __init__(self, game):
        # REFERENCE
        self.game = game  # Reference to Game class to access its attributes & methods

        # WINDOW SURFACE
        self.window_surface = pg.Surface((game.window.get_width(), game.window.get_height()))
        self.window_surface.fill(BLACK)  # Fill menu surface with a black background

        # BANNER
        self.banner_img = pg.image.load(join(BASE_IMG_DIR, 'menu', 'banner.png')).convert_alpha()
        self.select_marker_bomb_img = pg.image.load(join(BASE_IMG_DIR, 'menu',
                                                         'select_marker_bomb.png')).convert_alpha()
        self.defeat_face_img = pg.image.load(join(BASE_IMG_DIR, 'menu', 'defeat_face.png')).convert_alpha()
        self.defeat_face_img = pg.transform.smoothscale(self.defeat_face_img, (125, 125))

        # FONT
        self.menu_font = pg.font.Font(join(BASE_FONT_DIR, 'menu(upheaval-tt-brk).ttf'), 48)
        self.end_font = pg.font.Font(join(BASE_FONT_DIR, 'end(arkkos-gmimi).ttf'), 90)

        # COLOR
        self.menu_colors = [WHITE, BLUE]  # Colors used throughout the menu
        self.prev_action_color = self.menu_colors  # Variable stores the previous color of the selected action
        self.victorious_player_color = None  # Color for the victorious player (not set initially)

        # MAIN MENU SECTION
        self.main_menu_rects = []  # List used to store rect objects of the main menu options
        self.main_menu_options = ['1 Player', '2 Player', 'Settings', 'Exit']  # Options in main menu available to user
        self.in_main_menu = True  # Flag used to indicate user in the main section of the menu

        # SETTINGS SECTION
        self.settings_rects = []  # List used to store rect objects of the settings options
        self.settings_options = ['Customize Game', 'Audio', 'Controls',
                                 'Back']  # Options in settings menu section available to user
        self.in_settings = False  # Flag used to indicate user in settings section of the menu

        # CUSTOM SECTION
        self.custom_rects = []  # List used to store rect objects of the custom options
        self.custom_options_default = ['< Default >', 'Back']  # Default options in custom section available to the user
        self.custom_options_custom = ['< Custom >', 'Breakable Walls - < 00 >', 'Purple Creeps - < 00 >',
                                      'White Creeps - < 00 >', 'Red Creeps - < 00 >', 'Cyan Creeps - < 00 >',
                                      'Yellow Creeps - < 00 >',
                                      'Back']  # Customize options in custom section available to the user
        self.custom_options = self.custom_options_default  # Select default options as the starting custom options
        self.custom_mouse_nav_arrows_rects = []  # List that stores the mouse navigationa arrow rects for custom options
        self.rects_for_custom_arrows_added = False  # Flag used to signal if the mouse nav arrows were added to the list
        self.in_custom = False  # Flag used to indicate user in custom section of the menu
        self.customize_mode = False  # Flag used to indicate user in customize portion of the custom menu section

        # AUDIO SECTION
        self.audio_rects = []  # List used to store rect objects of the audio options
        self.audio_options = ['Music Volume - < 100% >', 'Soundeffects - < ON >', 'Back']  # Options for audio
        self.audio_mouse_nav_arrows_rects = []  # List that stores the mouse nav arrow rects for the audio options
        self.rects_for_audio_arrows_added = False  # Flag used to signal if the mouse nav arrows were added to the list
        self.in_audio = False  # Flag used to indicate user in audio section of the menu

        # CONTROLS SECTION
        self.controls_rects = []  # List used to store rect objects of the controls options
        self.controls_options_p1 = ['< Player 1 >', 'Up - < W >', ' Down - < S >',
                                    'Left - < A >', 'Right - < D >', 'Drop Bomb < SPACE >', 'Back']
        self.controls_options_p2 = ['< Player 2 >', 'Up - < UP >', ' Down - < DOWN >',
                                    'Left - < LEFT >', 'Right - < RIGHT >', 'Drop Bomb < L >', 'Back']
        self.controls_options = self.controls_options_p1  # Select Player 1 options as the starting controls options
        self.controls_mouse_nav_arrows_rects = []  # List that stores the mouse nav arrow rects for the controls options
        self.rects_for_controls_arrows_added = False  # Flag used to signal if mouse nav arrows were added to the list
        self.controls_arrow_rects_adjustable = False  # Flag used to signal nav arrows rects in controls are adjustable
        self.in_controls = False  # Flag used to indicate user in controls section of the menu

        # END SECTION
        self.end_surface = pg.Surface((464, 464), pg.SRCALPHA)  # Initialize a new surface for the end section
        self.end_surface_rect = self.end_surface.get_rect(  # Create a rect object for the end surface
            center=(self.game.window.get_width() // 2, self.game.window.get_height() // 2))
        self.end_surface.fill(BLACK)  # Fill end surface with a black background
        self.end_rects = []  # List used to store rect objects of the end options
        self.end_options = ['> Restart <', '> Main Menu <']  # Options for end section available to the user
        self.end_bg_fade_alpha = 255  # Initialize alpha value used to adjust transparency of the end surface background
        self.end_surface_delay_duration = 20  # Use a delay b4 displaying end surf on screen to avoid complications
        self.end_surface_delay_start_time = None  # Initialize a start time for the end surface delay
        self.in_end = False  # Flag used to signal user in end section of the menu

        # SELECTED ACTION INDEX
        self.selected_action_index = 0  # Index of the currently selected menu action
        self.prev_action_index = None  # Index of the previously selecteed menu action

        # MOUSE
        self.mouse_selecting = False  # Flag used to signal if mouse is currently selecting (initially set to False)
        self.last_mouse_pos = None  # Store the last position of the mouse
        self.on_mouse_hover_sound_played = False  # Flag use to indicate whether the mouse hover sound has been played
        self.sound_played_for_moused_rect = False  # Flag used to indicate if a sound was played for a mouse-overed rect
        self.last_select_sound_time = 0  # Store the time when the last selection sound was played

    # This function handles the drawing of the menu and updates dynamically
    def draw(self):

        # Render the menu window surface and banner on the game window unless menu is in the end section
        if not self.in_end:
            self.render_surface_and_banner(self.game.window, self.window_surface, self.banner_img)

        # Define a dictionary of menu sections and their corresponding options and rect objects
        menu_sections = {
            "main_menu": (self.main_menu_options, self.main_menu_rects),
            "settings": (self.settings_options, self.settings_rects),
            "custom": (self.custom_options, self.custom_rects),
            "audio": (self.audio_options, self.audio_rects),
            "controls": (self.controls_options, self.controls_rects),
            "end": (self.end_options, self.end_rects)
        }

        # Determine the current menu section
        current_menu_section = None
        if self.in_main_menu:
            current_menu_section = "main_menu"
        elif self.in_settings:
            current_menu_section = "settings"
        elif self.in_custom:
            current_menu_section = "custom"
        elif self.in_audio:
            current_menu_section = "audio"
        elif self.in_controls:
            current_menu_section = "controls"
        elif self.in_end:
            current_menu_section = "end"

            # If menu is in end section, render and display the end surface on the game window
            self.render_and_display_end_surface()

        # If the current menu section is defined, draw its options and selected action marker
        if current_menu_section in menu_sections:
            options, rects = menu_sections[current_menu_section]
            self.render_option_text_with_rect_and_layout(self.game.window, options, self.menu_font,
                                                         self.selected_action_index)

            # Render the selected action marker bomb on the game window unless menu is in the end section
            if not self.in_end:
                self.render_selected_action_index_marker_bomb(rects)

    # This function displays the menu window surface and the banner onto the game window
    def render_surface_and_banner(self, window, surface, banner_image):
        window.blit(surface, (0, 0))

        # Do not display game title banner in the following menu sections and modes
        if not (self.customize_mode or self.in_controls or self.in_end):
            window.blit(banner_image, (0, -20))

    # This function renders and displays an image marker used to indicate which option in the menu is currently selected
    def render_selected_action_index_marker_bomb(self, rects):
        # Ensure that the selected action index is within the bounds of the menu options
        if 0 <= self.selected_action_index < len(rects):
            # Get the rect corresponding to the currently selected menu option
            selected_action_rect = rects[self.selected_action_index]

            # Calculate the x and y coordinates for positioning the marker image to the left of the selected menu option
            marker_x = selected_action_rect.left - self.select_marker_bomb_img.get_width() - 10
            marker_y = selected_action_rect.centery - (self.select_marker_bomb_img.get_height() // 2) - 10

            # Display the marker image on the game window at the calculated position
            self.game.window.blit(self.select_marker_bomb_img, (marker_x, marker_y))

    # This function renders and displays the end surface, which shows the game outcome (victory, defeat, tie, etc.)
    def render_and_display_end_surface(self):

        # If the end surface delay start time is not set, get a start time timestamp when the method is called
        if self.end_surface_delay_start_time is None:
            self.end_surface_delay_start_time = pg.time.get_ticks()

        # Get the current time
        current_time = pg.time.get_ticks()

        # Check if the delay duration for displaying the end surface has passed
        if current_time - self.end_surface_delay_start_time < self.end_surface_delay_duration:
            return  # return if the delay duration has not passed yet

        # Draw the end surface on the game window with a blue outline around it
        pg.draw.rect(self.end_surface, BLUE, self.end_surface.get_rect(), 6)
        self.game.window.blit(self.end_surface, self.end_surface_rect)

        # For single-player mode, check each player's end information
        if self.game.game_mode_1player:
            for player_name, end_info in self.game.player_end_info_dict.items():

                # If the player collided with the exit portal/end point, render the victory screen
                if end_info['collided_with_ep']:
                    self.render_victory_screen(end_info)
                    return
                # If the player did not collide with the exit portal/end point, render the defeat screen
                else:
                    self.render_defeat_screen()

        # For two-player mode
        elif self.game.game_mode_2player:
            if not self.game.players:
                # If no players remain in game, check if ALL players have certain outcomes (explosion, collision, etc.)
                all_hit_by_explosion = all(
                    info.get('hit_by_bomb_explosion', True) for info in self.game.player_end_info_dict.values())
                all_collided_with_ep = all(
                    info.get('collided_with_ep', True) for info in self.game.player_end_info_dict.values())
                all_collided_with_creep = all(
                    info.get('collided_with_creep', True) for info in self.game.player_end_info_dict.values())

                # If all players experienced the same outcome, render the tie screen
                if all_hit_by_explosion or all_collided_with_ep or all_collided_with_creep:
                    self.render_tie_screen()
                    return

            # If players still exist, render the victory screen
            else:
                for player_name, end_info in self.game.player_end_info_dict.items():
                    self.render_victory_screen(end_info)
                    return

    # This function renders the victory screen, displaying "VICTORY" text along with the victorious player's color
    def render_victory_screen(self, end_info):

        # Create a dictionary mapping a color to their corresponding name
        color_mapping = {
            GREEN: "GREEN",
            BLUE: "BLUE"
        }

        # Determine the victorious player color based on game mode and player information
        if self.game.game_mode_1player:
            # For '1 Player' mode, there's only one player information retrieved in an end game event
            self.victorious_player_color = end_info['color']

        # For '2 Player' mode, trigger a check if there's only one player left in the game
        elif self.game.game_mode_2player:
            if len(self.game.players) == 1:
                # If that player did not collide with exit portal/end point
                for player_name, ending_info in self.game.player_end_info_dict.items():
                    if not ending_info['collided_with_ep']:
                        # Iterate through the remaining player in players list, that player color is victorious color
                        self.victorious_player_color = next(iter(self.game.players)).color

            # In any other event, the victorious player color is WHITE
            else:
                self.victorious_player_color = WHITE

        # Render "VICTORY" text string in WHTIE with end font as a surface
        text_victory_surface = self.end_font.render("VICTORY", True, WHITE)

        # Render the victorious color in a text string in appropriate color with end font as a surface
        text_victorious_color_surface = self.end_font.render(
            color_mapping.get(self.victorious_player_color) if self.victorious_player_color != WHITE else "VICTORY",
            True, self.victorious_player_color if self.victorious_player_color != WHITE else WHITE)

        # Create rect objects for both texts surfaces
        text_victory_rect = text_victory_surface.get_rect(
            center=(self.game.window.get_width() // 2, (self.game.window.get_height() // 3) - 40))
        text_victorious_color_rect = text_victorious_color_surface.get_rect(
            center=(self.game.window.get_width() // 2, (self.game.window.get_height() // 2) - 20))

        # Display the text surfaces with their rects on the game window
        self.game.window.blit(text_victory_surface, text_victory_rect)
        self.game.window.blit(text_victorious_color_surface, text_victorious_color_rect)

        # Play the end game victory soundeffect
        if not self.game.audio.victory_sfx_playing:
            self.game.audio.play_sfx('end_game_victory', volume=0.5)
            self.game.audio.victory_sfx_playing = True

    # This function renders the defeat screen, displaying "DEFEAT" text along with a defeat emoji
    def render_defeat_screen(self):

        # Render "DEFEAT" text string in WHTIE with end font as a surface and create a rect object for it
        text_defeat_surface = self.end_font.render("DEFEAT", True, WHITE)
        text_defeat_rect = text_defeat_surface.get_rect(
            center=(self.game.window.get_width() // 2, (self.game.window.get_height() // 3) - 40))

        # Create a rect object for the defeat face image and position the rect centrally with a bottom offset
        defeat_face_rect = self.defeat_face_img.get_rect()
        defeat_face_rect.center = (text_defeat_rect.centerx, text_defeat_rect.bottom + 90)

        # Display the text surface by its rect on the game window
        self.game.window.blit(text_defeat_surface, text_defeat_rect)
        self.game.window.blit(self.defeat_face_img, defeat_face_rect)

        # Play the end game defeat soundeffect
        if not self.game.audio.defeat_sfx_playing:
            self.game.audio.play_sfx('end_game_defeat', volume=0.5)
            self.game.audio.defeat_sfx_playing = True

    # This function renders the tie screen, indicating a tie game.
    def render_tie_screen(self):
        # Render the text "TIE !" using the end font and white color
        text_tie_surface = self.end_font.render("TIE !", True, WHITE)

        # Get the rect object representing the text surface and center it horizontally
        text_tie_rect = text_tie_surface.get_rect(
            center=(self.game.window.get_width() // 2, (self.game.window.get_height() // 2) - 20))

        # Display the text surface onto the game window at the specified rect position
        self.game.window.blit(text_tie_surface, text_tie_rect)

    # This function applies a fade effect to the end surface black background in order to make it see-through
    def apply_fade_effect_to_end_surface(self):
        # If mouse is hovered over the end surface
        if self.end_surface_rect.colliderect(pg.Rect(pg.mouse.get_pos(), (1, 1))):
            # Gradually decrease the alpha value
            self.end_bg_fade_alpha -= 3  # Adjust by decrement of 3 (-=3)
            self.end_bg_fade_alpha = max(127, self.end_bg_fade_alpha)  # ensure the alpha value doesn't go below 127
        else:
            # Gradually increase the alpha value
            self.end_bg_fade_alpha += 3  # Adjust by increment of 3 (+=3)
            self.end_bg_fade_alpha = min(255, self.end_bg_fade_alpha)  # ensure the alpha value doesn't exceed 255

        # Define a transparent color and pass the current alpha value inside
        transparent_color = pg.Color(0, 0, 0, self.end_bg_fade_alpha)

        # Fill the end surface window with the transparent color
        self.end_surface.fill(transparent_color)

    # This function handles the mouse selection rect lists for each option in each section of the menu
    def handle_mouse_selection(self):
        # Define a list containing all the rect lists
        all_rects_lists = [self.main_menu_rects, self.settings_rects, self.custom_rects,
                           self.audio_rects, self.controls_rects, self.end_rects,
                           self.audio_mouse_nav_arrows_rects, self.custom_mouse_nav_arrows_rects,
                           self.controls_mouse_nav_arrows_rects]

        # MAIN MENU SECTION
        if self.in_main_menu:
            # Retrieve the main menu rects from main menu options
            self.main_menu_rects = self.render_option_text_with_rect_and_layout(self.game.window,
                                                                                self.main_menu_options,
                                                                                self.menu_font,
                                                                                self.selected_action_index)
            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.main_menu_rects:
                    rects_list.clear()

        # SETTINGS MENU SECTION
        elif self.in_settings:
            # Retrieve the settings rects from settings options
            self.settings_rects = self.render_option_text_with_rect_and_layout(self.game.window,
                                                                               self.settings_options,
                                                                               self.menu_font,
                                                                               self.selected_action_index)

            # Reset all mouse nav arrow flags when going back to settings from either custom, audio or controls sections
            self.rects_for_custom_arrows_added = False
            self.rects_for_audio_arrows_added = False
            self.rects_for_controls_arrows_added = False

            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.settings_rects:
                    rects_list.clear()

        # CUSTOM MENU SECTION
        elif self.in_custom:
            # Retrieve the custom rects from custom options
            self.custom_rects = self.render_option_text_with_rect_and_layout(self.game.window, self.custom_options,
                                                                             self.menu_font, self.selected_action_index)

            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.custom_rects and not self.custom_mouse_nav_arrows_rects:
                    rects_list.clear()

            # Check if mouse arrow nav rects for custom options haven't been added yet or if currently in customize mode
            if not self.rects_for_custom_arrows_added or self.customize_mode:
                del self.custom_mouse_nav_arrows_rects[:]  # clear the existing custom mouse nav arrow rects list

                # Define the initial y-position for arrow rects (101 if customize mode, else 333)
                y_pos = 333 if not self.customize_mode else 101

                # Create the rect objects for the mouse navigation arrows in the custom menu section
                self.create_arrow_rects_for_options(options=self.custom_options,
                                                    rects=self.custom_mouse_nav_arrows_rects,
                                                    y_pos=y_pos,
                                                    y_step=60)

                # Update the flag indicating whether arrow rects for custom options have been added
                self.rects_for_custom_arrows_added = not self.customize_mode

        # AUDIO MENU SECTION
        elif self.in_audio:
            # Retrieve the audio rects from audio options
            self.audio_rects = self.render_option_text_with_rect_and_layout(self.game.window, self.audio_options,
                                                                            self.menu_font, self.selected_action_index)

            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.audio_rects and not self.audio_mouse_nav_arrows_rects:
                    rects_list.clear()

            # If the rects for the mouse nav arrows in audio section haven't been added yet, create and add them
            if not self.rects_for_audio_arrows_added:
                self.create_arrow_rects_for_options(options=self.audio_options,
                                                    rects=self.audio_mouse_nav_arrows_rects,
                                                    y_pos=311,
                                                    y_step=60)

                self.rects_for_audio_arrows_added = True  # set flag used to signal if arrows have been added to True

        # CONTROLS MENU SECTION
        elif self.in_controls:
            # Retrieve the controls rects from controls options
            self.controls_rects = self.render_option_text_with_rect_and_layout(self.game.window, self.controls_options,
                                                                               self.menu_font,
                                                                               self.selected_action_index)

            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.controls_rects and not self.controls_mouse_nav_arrows_rects:
                    rects_list.clear()

            # If the rects for the mouse nav arrows in controls section haven't been added yet, create and add them
            if not self.rects_for_controls_arrows_added:
                self.create_arrow_rects_for_options(options=self.controls_options,
                                                    rects=self.controls_mouse_nav_arrows_rects,
                                                    y_pos=133,
                                                    y_step=60)

                self.rects_for_controls_arrows_added = True  # set flag used to signal if arrows have been added to True
                self.controls_arrow_rects_adjustable = True  # set flag used to signal if arrows are adjustable to True

            # If arrows being adjustable is True, create and adjust the arrow rects according to the method
            if self.controls_arrow_rects_adjustable:
                for i, (left_arrow_rect, right_arrow_rect) in enumerate(self.controls_mouse_nav_arrows_rects):
                    # FOR DEBUGGING /// Uncomment to check if assignment was successful
                    # pg.draw.rect(self.window_surface, BLACK, left_arrow_rect)
                    # pg.draw.rect(self.window_surface, BLACK, right_arrow_rect)

                    # Get the x coordinate values for the arrow rects in controls options
                    left_arrow_x, right_arrow_x = self.calculate_x_value_of_arrows_rects_for_controls(arrow_index=i)
                    left_arrow_rect.x = left_arrow_x
                    right_arrow_rect.x = right_arrow_x

                    # FOR DEBUGGING /// Uncomment to check if assignment was successful
                    # Redraw the rectangles with updated positions
                    # left_arrow_color = (255, 0, 0)
                    # right_arrow_color = (0, 255, 0)
                    # pg.draw.rect(self.window_surface, left_arrow_color, left_arrow_rect)
                    # pg.draw.rect(self.window_surface, right_arrow_color, right_arrow_rect)

                    # Print the updated x-coordinates with index information
                    # print(f"Index {i}: Left Arrow Rect X:", left_arrow_rect.x)
                    # print(f"Index {i}: Right Arrow Rect X:", right_arrow_rect.x)

        # END MENU SECTION
        elif self.in_end:
            # Retrieve the end rects from end options
            self.end_rects = self.render_option_text_with_rect_and_layout(self.game.window, self.end_options,
                                                                          self.menu_font, self.selected_action_index)
            # Apply the face effect to the background of the end surface
            self.apply_fade_effect_to_end_surface()

            # Clear all text rect objects except the current section ones
            for rects_list in all_rects_lists:
                if rects_list is not self.end_rects:
                    rects_list.clear()

    # This function renders each option of a section together w/ its rect and determines the color and layout
    def render_option_text_with_rect_and_layout(self, window, options, font, selected_index):
        banner_height = self.banner_img.get_height()  # get the height of the banner image
        font_height = font.get_height()  # get the height of the font used for options text
        menu_options_height = len(options) * font_height  # determine total height occupied by all options
        vertical_space = window.get_height() - banner_height  # vertical space available for rendering options
        starting_vert_pos = ((vertical_space - menu_options_height) // 2) - 80  # vertical pos for the first option
        between_spacing = 16  # spacing between each option

        # Adjust the starting vertical position for specific menu sections that will deviate from the deafult position
        if self.customize_mode:
            starting_vert_pos = ((vertical_space - menu_options_height) // 2) - 180

        elif self.in_controls:
            starting_vert_pos = ((vertical_space - menu_options_height) // 2) - 170

        elif self.in_end:
            starting_vert_pos = ((vertical_space - menu_options_height) // 2)

        # Define a list used to store the rect objects of each rendered option text
        text_rects = []

        # Iterate through the number of available options in any given menu section
        for i, option in enumerate(options):
            # Determine color based on whether the option is selected or not
            color = self.menu_colors[1] if i == selected_index else self.menu_colors[0]

            # Render the option text surface using the slected font and color
            text_surface = font.render(option, True, color)

            # Calculate the rect object for the rendered text, centered horizontally and vertically positioned
            text_rect = text_surface.get_rect(center=(window.get_width() // 2,
                                                      banner_height + starting_vert_pos + i *
                                                      (font_height + between_spacing)))

            # Display the text surface onto the menu window surface at the calculated position
            window.blit(text_surface, text_rect)
            text_rects.append(text_rect)  # append the text rectangle to the list

        # Return the list of rectangles for each option text
        return text_rects

    # This function replaces a string in an individual option with another string when left or right key is pressed
    def replace_string_in_option(self, option, key_pressed=None):
        if key_pressed == pg.K_RIGHT or key_pressed == pg.K_LEFT:

            # Change 'ON' to 'OFF'
            if "< ON >" in option:
                return option.replace("< ON >", "< OFF >")

            # Change 'OFF' to 'ON'
            elif "< OFF >" in option:
                return option.replace("< OFF >", "< ON >")

            # Change 'Default' to 'Custom' and set options list as the custom list
            elif "< Default >" in option:
                self.customize_mode = True  # flag used to signal user is in custom part of the section
                option = option.replace("< Default >", "< Custom >")
                self.custom_options = self.custom_options_custom

            # Change 'Custom' to 'Default' and set options list as the default list
            elif "< Custom >" in option:
                self.customize_mode = False  # flag used to signal user is NOT in custom part of the section
                option = option.replace("< Custom >", "< Default >")
                self.custom_options = self.custom_options_default

            # Change 'Player 1' to 'Player 2' and set controls options list as the Player 2 list
            elif "< Player 1 >" in option:
                option = option.replace("< Player 1 >", "< Player 2 >")
                self.controls_options = self.controls_options_p2

            # Change 'Player 2' to 'Player 1' and set controls options list as the Player 1 list
            elif "< Player 2 >" in option:
                option = option.replace("< Player 2 >", "< Player 1 >")
                self.controls_options = self.controls_options_p1

        # Return the replaced option new value
        return option

    # This function handles the logic for scrolling through the custom options in the custom menu section
    def scroll_custom_option(self, index, increment_amount, key_pressed=None):
        # Store the custom option with index passed as an argument into custom option variable
        custom_option = self.custom_options[index]
        parts = custom_option.split()  # split the custom option variable by its space to extract the number part
        number_part = parts[-2]  # get the second-to-last part of the number part

        # Max number you can stroll to is 10 unless the string at index 1 matches 'Walls', then max number is 99
        max_number = 99 if parts[1] == 'Walls' else 10
        current_number_str = number_part.strip('<>%')  # remove the '<' and '>' characters and extract the number value

        # Depending on the number inside the string and the key press, set value accordingly
        if current_number_str == '00':
            if key_pressed == pg.K_LEFT:
                return custom_option.replace('00', '99' if max_number == 99 else '10')

            elif key_pressed == pg.K_RIGHT:
                return custom_option.replace('00', '01')

        elif current_number_str == '99':
            if key_pressed == pg.K_LEFT:
                return custom_option.replace('99', '98')

            elif key_pressed == pg.K_RIGHT:
                return custom_option.replace('99', '00')

        elif current_number_str == '10':
            if key_pressed == pg.K_LEFT:
                return custom_option.replace('10', '09')

            elif key_pressed == pg.K_RIGHT:
                return custom_option.replace('10', '00' if not max_number == 99 else '11')

        # Convert the numerical string number value into an integer
        current_number = int(current_number_str)

        # Increment or decrement the number by the specified amount, ensuring it stays within the range
        new_number = max(0, min(max_number, current_number + increment_amount))

        # Update custom option w/ new value using zfill to fill zeroes up front when number has less than two digits
        return custom_option.replace(current_number_str.zfill(2), str(new_number).zfill(2))

    # This function handles the logic for adjusting the volume of the in game music through the audio menu section
    def adjust_volume_option(self, index, increment_amount, key_pressed=None):
        # Store the audio option with index passed as an arguement into custom option variable
        volume_option = self.audio_options[index]
        parts = volume_option.split()  # split the custom option variable by its space to extract the number part
        percentage_part = parts[-2]  # get the second-to-last part of the number part

        # Remove the '<' and '>' characters and extract the percentage value
        current_percentage_str = percentage_part.strip('<>%')

        # If current percentage string is 'OFF'
        if current_percentage_str == 'OFF':
            # If RIGHT arrow key pressed, string changed to 100%, if LEFT key pressed, string changes to 10%
            return 'Music Volume - < 100% >' if key_pressed == pg.K_RIGHT else 'Music Volume - < 10% >'

        # If current percentage string is '100'
        elif current_percentage_str == '100':
            # If LEFT arrow key pressed, string changed to OFF, if RIGHT key pressed, string changes to 90%
            return 'Music Volume - < OFF >' if key_pressed == pg.K_LEFT else 'Music Volume - < 90% >'

        else:
            # Convert the numerical value to an integer
            current_percentage = int(current_percentage_str)

            # Increment or decrement the volume by the specified amount, ensuring it stays within 0 to 100
            new_percentage = max(0, min(100, current_percentage + increment_amount))

            # Update the volume option string accordingly (0% == OFF, else return new percentage)
            if new_percentage == 0:
                return 'Music Volume - < OFF >'
            else:
                return f'Music Volume - < {new_percentage}% >'

    # This function handles the logic for scrolling thorugh the controls options in the controls menu section
    def scroll_controls_option(self, index, key_pressed=None):
        # Store the control option with index passed as an arguement into custom option variable
        control_option = self.controls_options[index]
        input_key = control_option.split('<')[-1].split('>')[0].strip().lower()  # split string to obtain key part
        all_keys = ALPHABET_INPUT_KEYS + OTHER_INPUT_KEYS  # get all possible control keys

        # Check if the control key is in the list of all keys
        if input_key in all_keys:
            current_index = all_keys.index(input_key)  # get the current index of the control key

            # Calculate new index based on the key pressed
            new_index = (current_index - 1) if key_pressed == pg.K_LEFT else (current_index + 1)
            new_key = all_keys[new_index % len(all_keys)]

            # Replace the old key with the new key and update the control option string at the index passed as arguement
            self.controls_options[index] = control_option.replace(f'< {input_key.upper()} >',
                                                                  f'< {new_key.upper()} >')

    # This function creates arrow rects for controls options that adjust their position on the window
    def calculate_x_value_of_arrows_rects_for_controls(self, arrow_index):

        # Base x-coordinate values for the left & right arrow rects depending on the control option index for Player 1
        p1_base_x_values = {
            0: (543, 811),
            1: (695, 780),
            2: (735, 819),
            3: (723, 807),
            4: (735, 819),
            5: (770, 854)
        }
        # Base x-coordinate values for the left & right arrow rects depending on the control option index for Player 2
        p2_base_x_values = {
            0: (543, 811),
            1: (695, 780),
            2: (735, 820),
            3: (723, 807),
            4: (735, 819),
            5: (771, 853)}

        # Initialize a dictionary as a placeholder for the current base x-coordinate values list
        current_base_x_values = {}
        difference_at_index = {2: 12, 3: 26, 4: 44, 5: 56, 6: 70}  # map the index & difference in x-coordinate values
        left_arrow_x, right_arrow_x = 0, 0  # create variables that store the x coordiante values for left & right arrow

        # If the current arrow index does not surpass the length of the control options
        if arrow_index < len(self.controls_options):
            left_arrow_index = self.controls_options[arrow_index].find('<')
            right_arrow_index = self.controls_options[arrow_index].find('>')
            control_string = self.controls_options[arrow_index].split('<')[-1].split('>')[0].strip()
            num_letters = len(control_string)

            # If both left and right arrows are found in the control option string
            if left_arrow_index != -1 and right_arrow_index != -1:
                # Check if controls_options[0] is '< Player 1 >'
                if self.controls_options[0] == '< Player 1 >':
                    current_base_x_values = p1_base_x_values
                # Check if controls_options[0] is '< Player 2 >'
                elif self.controls_options[0] == '< Player 2 >':
                    current_base_x_values = p2_base_x_values

                # If the arrow_index is in the base_x_values dictionary
                if arrow_index in current_base_x_values:
                    left_arrow_x, right_arrow_x = current_base_x_values[arrow_index]

                    # Adjust arrow positions based on the number of letters in the control string
                    if num_letters in difference_at_index:
                        difference = difference_at_index[num_letters]
                        left_arrow_x -= difference
                        right_arrow_x += difference

        # Return the left and right arrow x coordinate values
        return left_arrow_x, right_arrow_x

    # This function creates arrow rects for the audio and controls options
    def create_arrow_rects_for_options(self, options, rects, y_pos, y_step):
        # Define a standardized width and height for the arrow rects
        rect_width = 36
        rect_height = 26

        # Define the x and y positions of the arrow rects for different menu section options
        arrow_positions = {
            'audio_options': {
                0: (809, 951),
                1: (817, 945)
            },
            'custom_options': {
                0: (550, 803) if not self.customize_mode else (562, 792),
                1: (868, 980),
                2: (834, 947),
                3: (820, 932),
                4: (792, 904),
                5: (807, 918),
                6: (838, 950)}
        }

        # Iterate over each option and find the indices of the left and right arrows in the option string
        for i in range(len(options)):
            left_arrow_index = options[i].find('<')
            right_arrow_index = options[i].find('>')
            left_arrow_x, right_arrow_x = 0, 0  # store the x coordiante values for left & right arrow

            # If both left and right arrows are found in the control option string
            if left_arrow_index != -1 and right_arrow_index != -1:
                # Determine the type of option (audio or custom)
                option_type = 'audio_options' if options == self.audio_options else 'custom_options'
                if i in arrow_positions[option_type]:
                    left_arrow_x, right_arrow_x = arrow_positions[option_type][i]

                # Create a rect object for both the left and righ arrow and append them to a list passed as an arg
                left_arrow_rect = pg.Rect((left_arrow_x, y_pos, rect_width, rect_height))
                right_arrow_rect = pg.Rect((right_arrow_x, y_pos, rect_width, rect_height))
                rects.append((left_arrow_rect, right_arrow_rect))

                # FOR DEBUGGING /// Uncomment to check if code runs as intended
                # left_arrow_color = (255, 0, 0)
                # right_arrow_color = (0, 255, 0)
                # pg.draw.rect(self.window_surface, left_arrow_color, left_arrow_rect)
                # pg.draw.rect(self.window_surface, right_arrow_color, right_arrow_rect)
                # print("Left Arrow X Position:", left_arrow_x)
                # print("Right Arrow X Position:", right_arrow_x)

            # Increment y_position by y_step for subsequent options
            y_pos += y_step

    # This function iterates through all the rects in a menu section & checks what rect index is colliding with cursor
    def check_cursor_collision(self, cursor_pos):
        # Combine all rects from different menu sections into one list
        all_rects = self.main_menu_rects + self.settings_rects + \
                    self.custom_rects + self.audio_rects + self.controls_rects + self.end_rects

        cursor_set = False  # flag to keep track if cursor has been set

        # Iterate through all rects and check for collision with the cursor
        for i, rect in enumerate(all_rects):
            if rect.collidepoint(cursor_pos):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)  # set cursor to 'hand' symbol if collision is detected
                return i  # return the index of the collided rect

        # If no collision is detected, set cursor to default arrow cursor and return None index
        if not cursor_set:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            return None

    # This function handles all the main events like (mouse and keyboard interactions) inside the menu class
    def handle_events(self, events, rects, options):

        # Check for events
        for event in events:

            # LEFT MOUSE BUTTON CLICK (DOWN)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_action_index = self.check_cursor_collision(event.pos)  # check cursor collision
                # Set the mouse selected action index to the current selected action index
                if mouse_action_index is not None:
                    self.selected_action_index = mouse_action_index
                    self.mouse_selecting = True  # set flag used to indicate mouse is selecting to True

                    # Check the current menu state and execute corresponding actions
                    if self.in_main_menu:
                        self.main_menu_actions(self.selected_action_index)
                    elif self.in_settings:
                        self.settings_actions(self.selected_action_index)
                    elif self.in_custom:
                        self.custom_actions(self.selected_action_index)

                        # Extract left and right arrow rects from the custom mouse nav arrows rects list
                        for left_arrow_rect, right_arrow_rect in self.custom_mouse_nav_arrows_rects:
                            # Check if the cursor collides with any of the arrow rects
                            if left_arrow_rect.collidepoint(event.pos) or right_arrow_rect.collidepoint(event.pos):

                                # Determine the index of the arrow being clicked
                                arrow_index = self.custom_mouse_nav_arrows_rects.index(
                                    (left_arrow_rect, right_arrow_rect))

                                # Determine the scroll direction based on which arrow is clicked
                                scroll_direction = pg.K_LEFT if left_arrow_rect.collidepoint(event.pos) else pg.K_RIGHT

                                # Determine the scroll amount
                                scroll_amount = -1 if scroll_direction == pg.K_LEFT else 1

                                # Update the corresponding custom option based on the arrow index
                                if arrow_index == 0:
                                    # If it's the first arrow, update the option directly by replacing strings
                                    self.custom_options[0] = self.replace_string_in_option(self.custom_options[0],
                                                                                           scroll_direction)
                                else:
                                    # If it's any other arrow, scroll the custom option
                                    self.custom_options[arrow_index] = self.scroll_custom_option(arrow_index,
                                                                                                 scroll_amount,
                                                                                                 scroll_direction)
                                # Play the menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    elif self.in_audio:
                        self.audio_actions(self.selected_action_index)

                        # Extract left and right arrow rects from the audio mouse nav arrows rects list
                        for left_arrow_rect, right_arrow_rect in self.audio_mouse_nav_arrows_rects:
                            # Check if the cursor collides with any of the arrow rects
                            if left_arrow_rect.collidepoint(event.pos) or right_arrow_rect.collidepoint(event.pos):

                                # Determine the index of the arrow being clicked
                                arrow_index = self.audio_mouse_nav_arrows_rects.index(
                                    (left_arrow_rect, right_arrow_rect))

                                # Determine the scroll direction based on the arrow clicked
                                scroll_direction = pg.K_LEFT if left_arrow_rect.collidepoint(
                                    event.pos) else pg.K_RIGHT

                                # Determine the scroll amount
                                scroll_amount = -10 if scroll_direction == pg.K_RIGHT else 10

                                # If it's the first arrow, adjust the volume option
                                if arrow_index == 0:
                                    self.audio_options[0] = self.adjust_volume_option(arrow_index, scroll_amount,
                                                                                      scroll_direction)
                                # Else replace the string in option
                                elif arrow_index == 1:
                                    self.audio_options[1] = self.replace_string_in_option(self.audio_options[1],
                                                                                          scroll_direction)
                                # Play the menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    elif self.in_controls:
                        self.controls_actions(self.selected_action_index)

                        # Extract left and right arrow rects from the controls mouse nav arrows rects list
                        for left_arrow_rect, right_arrow_rect in self.controls_mouse_nav_arrows_rects:
                            # Check if the cursor collides with any of the arrow rects
                            if left_arrow_rect.collidepoint(event.pos) or right_arrow_rect.collidepoint(event.pos):

                                # Determine the index of the arrow being clicked
                                arrow_index = self.controls_mouse_nav_arrows_rects.index(
                                    (left_arrow_rect, right_arrow_rect))

                                # Determine the scroll direction
                                scroll_direction = pg.K_LEFT if left_arrow_rect.collidepoint(event.pos) else pg.K_RIGHT

                                # If index in arrows list equals 0, replace string in option with new string
                                if arrow_index == 0:
                                    self.controls_options[0] = self.replace_string_in_option(self.controls_options[0],
                                                                                             scroll_direction)
                                # Else use the method to scroll through controsl option
                                else:
                                    self.scroll_controls_option(arrow_index, scroll_direction)

                                # Play the menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    elif self.in_end:
                        self.end_actions(self.selected_action_index)

            # LEFT MOUSE BUTTON CLICK (UP)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.mouse_selecting = False  # set flag indicating that the mouse is selecting to False

            # MOUSE ON HOVER (Handle in event of mouse cursor hovering over target)
            elif event.type == pg.MOUSEMOTION:

                # Check cursor collision to obtain index based on mouse position
                mouse_action_index = self.check_cursor_collision(event.pos)
                mouse_pos = pg.mouse.get_pos()  # get current mouse position

                # Initialize colors list with the same length as rects
                colors = [WHITE] * len(rects)

                # Iterate through each rect object in menu section and update the text color if hovered by mouse
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        colors[i] = BLUE  # if hovered, set the color to blue

                # Update selected action index if mouse action index is valid
                if mouse_action_index is not None and 0 <= mouse_action_index < len(colors):
                    self.selected_action_index = mouse_action_index

                # Update previous action index and color
                if 0 <= self.selected_action_index < len(colors):
                    if self.selected_action_index != self.prev_action_index:  # check if the selected index has changed
                        self.on_mouse_hover_sound_played = False

                self.prev_action_index = self.selected_action_index  # update previous action index

                if 0 <= self.selected_action_index < len(colors):
                    self.prev_action_color = colors[self.selected_action_index]  # store olor of the selected action

                    if colors[self.selected_action_index] == BLUE:  # check if the selected action is blue (hovered)
                        current_time = pg.time.get_ticks()  # get the current time
                        if (
                                mouse_pos != self.last_mouse_pos
                                and not self.sound_played_for_moused_rect
                                and current_time - self.last_select_sound_time >= 100
                        ):
                            self.game.audio.play_sfx('menu_nav', volume=0.3)

                            self.sound_played_for_moused_rect = True  # set sound flag for the current rect as True
                            self.last_select_sound_time = current_time  # update the last select sound time
                    else:
                        self.sound_played_for_moused_rect = False  # reset sound flag when text is not orange

                    self.last_mouse_pos = mouse_pos  # update the last mouse position

            # KEYBOARD KEYS PRESSED (DOWN)
            elif event.type == pg.KEYDOWN:

                # RETURN/ENTER
                if event.key == pg.K_RETURN:
                    # Execute the following action methods based on the menu section's selected action index
                    if self.in_main_menu:
                        self.main_menu_actions(self.selected_action_index)
                    elif self.in_settings:
                        self.settings_actions(self.selected_action_index)
                    elif self.in_custom:
                        self.custom_actions(self.selected_action_index)
                    elif self.in_audio:
                        self.audio_actions(self.selected_action_index)
                    elif self.in_controls:
                        self.controls_actions(self.selected_action_index)
                    elif self.in_end:
                        self.end_actions(self.selected_action_index)

                # LEFT KEY
                elif event.key == pg.K_LEFT:
                    # If in custom section of the menu
                    if self.in_custom:
                        # If in custom portion of custom menu, create a list with scroll indices
                        if self.customize_mode:
                            scroll_indices = [0, 1, 2, 3, 4, 5, 6]
                        # Else, if default portion, only index is 0
                        else:
                            scroll_indices = [0]

                        # Iterate through all the indices in scroll indices
                        for index in scroll_indices:
                            # If index equals the current selection action index
                            if self.selected_action_index == index:
                                # When it equals 0, replace string in custom options (default/custom)
                                if index == 0:
                                    self.custom_options[index] = self.replace_string_in_option(
                                        self.custom_options[index], pg.K_LEFT)
                                # Else, run the function that scrolls through custom options
                                else:
                                    self.custom_options[index] = self.scroll_custom_option(index, -1, pg.K_LEFT)

                                # Play menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    # Else, If in audio section of the menu
                    elif self.in_audio:
                        # If audio options index 0 is equal to current selected action index
                        if self.selected_action_index == 0:
                            # Run function that adjust the game volume
                            self.audio_options[0] = self.adjust_volume_option(self.selected_action_index, 10, pg.K_LEFT)

                            # Play menu adjust soundeffect
                            self.game.audio.play_sfx('menu_adjust', volume=0.9)

                        # Else, if audio options index 1 is equal to current selected action index
                        elif self.selected_action_index == 1:
                            # Replace string at audio options index 1 (yes/no)
                            self.audio_options[1] = self.replace_string_in_option(self.audio_options[1], pg.K_LEFT)

                            # Play menu adjust soundeffect
                            self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    # Else, if in controls menu section
                    elif self.in_controls:
                        scroll_indices = [0, 1, 2, 3, 4, 5]

                        # Iterate through the indices in the controls menu options
                        for index in scroll_indices:
                            if self.selected_action_index == index:
                                # If selected action index is 0
                                if index == 0:
                                    # Replace controls option stsring (player 1/player 2)
                                    self.controls_options[index] = self.replace_string_in_option(
                                        self.controls_options[index], pg.K_LEFT)
                                # Other indices, run function that scrolls through controls options
                                else:
                                    self.scroll_controls_option(index, pg.K_LEFT)

                                # Play menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                # RIGHT KEY
                elif event.key == pg.K_RIGHT:
                    # If in custom menu section
                    if self.in_custom:
                        # If in customize portion of custom menu, create a list with scroll indices
                        if self.customize_mode:
                            scroll_indices = [0, 1, 2, 3, 4, 5, 6]
                        # Else in default portion of custom menu
                        else:
                            scroll_indices = [0]

                        # Iterate through the indices in the custom menu options
                        for index in scroll_indices:
                            if self.selected_action_index == index:
                                # If index equals 0, replace string in option (switch between default/custom)
                                if index == 0:
                                    self.custom_options[index] = self.replace_string_in_option(
                                        self.custom_options[index], pg.K_RIGHT)
                                # Else, scroll through custom option
                                else:
                                    self.custom_options[index] = self.scroll_custom_option(index, 1, pg.K_RIGHT)

                                # Play menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    # Else, if in audio menu section
                    elif self.in_audio:
                        # If selected action index is 0
                        if self.selected_action_index == 0:
                            # Adjust music volume
                            self.audio_options[0] = self.adjust_volume_option(self.selected_action_index,
                                                                              -10, pg.K_RIGHT)

                            # Play menu adjust soundeffect
                            self.game.audio.play_sfx('menu_adjust', volume=0.9)

                        # Else, if selected action index is 1
                        elif self.selected_action_index == 1:
                            # Replace string in option (yes/no to enable soundeffects)
                            self.audio_options[1] = self.replace_string_in_option(self.audio_options[1], pg.K_RIGHT)

                            # Play menu adjust soundeffect
                            self.game.audio.play_sfx('menu_adjust', volume=0.9)

                    # Else, if in controls menu section
                    elif self.in_controls:
                        scroll_indices = [0, 1, 2, 3, 4, 5]

                        # Iterate through the indices in the controls menu options
                        for index in scroll_indices:
                            if self.selected_action_index == index:
                                # If selected action index is 0
                                if index == 0:
                                    # If index is 0, replace string in option (switch between player 1/player 2 options)
                                    self.controls_options[index] = self.replace_string_in_option(
                                        self.controls_options[index], pg.K_RIGHT)
                                # Else, scroll through controls option
                                else:
                                    self.scroll_controls_option(index, pg.K_RIGHT)

                                # Play menu adjust soundeffect
                                self.game.audio.play_sfx('menu_adjust', volume=0.9)

                # UP KEY
                elif event.key == pg.K_UP:
                    # If UP key is pressed, DEcrement action index by 1, wrap around to the end of list if necessary
                    self.selected_action_index = (self.selected_action_index - 1) % len(options)
                    self.game.audio.play_sfx('menu_nav', volume=0.3)  # Play menu navigaton soundeffect

                # DOWN KEY
                elif event.key == pg.K_DOWN:
                    # If UP key is pressed, Increment action index by 1, wrap around to the end of list if necessary
                    self.selected_action_index = (self.selected_action_index + 1) % len(options)
                    self.game.audio.play_sfx('menu_nav', volume=0.3)  # Play menu navigaton soundeffect

    # This function handles the state of various flags and variables when the user switches to the main menu
    def switch_to_main_menu(self):
        self.game.in_menu = True
        self.in_main_menu = True
        self.in_settings = False
        self.in_audio = False
        self.in_controls = False
        self.in_custom = False
        self.in_end = False
        self.game.game_mode_1player = False
        self.game.game_mode_2player = False
        self.selected_action_index = 0
        self.game.audio.stop_all_sfx()

    # This function handles the state of various flags and variables when the user switches to the settings menu
    def switch_to_settings(self):
        self.game.in_menu = True
        self.in_settings = True
        self.in_main_menu = False
        self.in_audio = False
        self.in_custom = False
        self.customize_mode = False
        self.in_controls = False
        self.selected_action_index = 0

    # This function handles the state of various flags and variables when the user switches to the custom menu
    def switch_to_custom(self):
        self.game.in_menu = True
        self.in_custom = True
        self.in_main_menu = False
        self.in_settings = False
        self.in_audio = False
        self.in_controls = False
        self.selected_action_index = 0

    # This function handles the state of various flags and variables when the user switches to the audio menu
    def switch_to_audio(self):
        self.game.in_menu = True
        self.in_audio = True
        self.in_main_menu = False
        self.in_settings = False
        self.in_custom = False
        self.in_controls = False
        self.selected_action_index = 0

    # This function handles the state of various flags and variables when the user switches to the controls menu
    def switch_to_controls(self):
        self.game.in_menu = True
        self.in_controls = True
        self.in_main_menu = False
        self.in_settings = False
        self.in_audio = False
        self.in_custom = False
        self.selected_action_index = 0

    # This function handles the state of various flags and variables when the user switches to the end menu
    def switch_to_end(self):
        self.in_end = True
        self.game.in_menu = False
        self.in_main_menu = False
        self.in_settings = False
        self.in_custom = False
        self.in_controls = False
        self.in_audio = False
        self.selected_action_index = 0

    # This function handles what happens when the user selects a particular index inside the main menu
    def main_menu_actions(self, i):
        play_menu_confirm_sfx = False
        if i == 0:
            play_menu_confirm_sfx = True
            self.game.in_menu = False
            self.in_main_menu = False
            self.game.game_mode_1player = True
            self.game.game_mode_2player = False
            self.game.new_game()
        elif i == 1:
            play_menu_confirm_sfx = True
            self.game.in_menu = False
            self.in_main_menu = False
            self.game.game_mode_1player = False
            self.game.game_mode_2player = True
            self.game.new_game()
        elif i == 2:
            play_menu_confirm_sfx = True
            self.in_main_menu = False
            self.switch_to_settings()
        elif i == 3:
            pg.quit()
            sys.exit()

        if play_menu_confirm_sfx:
            self.game.audio.play_sfx('menu_confirm', volume=0.6)

    # This function handles what happens when the user selects a particular index inside the settings menu
    def settings_actions(self, i):
        play_menu_confirm_sfx = False
        if i == 0:
            play_menu_confirm_sfx = True
            self.switch_to_custom()
            if self.custom_options[0] == '< Custom >':
                self.customize_mode = True
        elif i == 1:
            play_menu_confirm_sfx = True
            self.switch_to_audio()
        elif i == 2:
            play_menu_confirm_sfx = True
            self.switch_to_controls()
        elif i == len(self.settings_options) - 1:
            play_menu_confirm_sfx = True
            self.switch_to_main_menu()

        if play_menu_confirm_sfx:
            self.game.audio.play_sfx('menu_confirm', volume=0.6)

    # This function handles what happens when the user selects a particular index inside the custom menu
    def custom_actions(self, i):
        if i == len(self.custom_options) - 1:
            self.game.audio.play_sfx('menu_confirm', volume=0.6)
            self.switch_to_settings()

    # This function handles what happens when the user selects a particular index inside the audio menu
    def audio_actions(self, i):
        if i == len(self.audio_options) - 1:
            self.game.audio.play_sfx('menu_confirm', volume=0.6)
            self.switch_to_settings()

    # This function handles what happens when the user selects a particular index inside the controls menu
    def controls_actions(self, i):
        if i == len(self.controls_options) - 1:
            self.game.audio.play_sfx('menu_confirm', volume=0.5)
            self.switch_to_settings()

    # This function handles what happens when the user selects a particular index inside the end menu
    def end_actions(self, i):
        play_menu_confirm_sfx = False
        if i == 0:
            play_menu_confirm_sfx = True
            self.game.new_game()
            self.game.in_menu = False
            self.in_end = False
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            pg.mixer.music.rewind()
        elif i == len(self.end_options) - 1:
            play_menu_confirm_sfx = True
            self.switch_to_main_menu()

        if play_menu_confirm_sfx:
            self.game.audio.play_sfx('menu_confirm', volume=0.6)

        self.game.audio.stop_all_sfx()  # stop any soundeffects that are still playing

    # This function handles dynamic updates for the menu object
    def update(self):
        self.handle_mouse_selection()
