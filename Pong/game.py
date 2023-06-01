# Pong/game.py
from setup import pg, setup_pygame, access_window, access_clock, render_display
from constants import WHITE, SUNSET_ORANGE
from game_modes import two_player_mode, pause_game, reset_game, exit_game
from sound import play_menu_music, play_game_music
from menu import menu

window = access_window()  # access game window


class Pong:
    def __init__(self):
        setup_pygame()  # setup pygame
        access_window()  # access window
        access_clock()  # access clock

        self.in_menu = True  # set in_menu flag attribute as True (currently in menu)
        self.in_game = False  # set in_game flag attribute as True (currently NOT in game)
        self.new_game_started = False  # set new_game_starteed flag attribute as False (game NOT yet started)

        self.action_index = 0  # define int variable to track which action is being performed based on its index
        self.mouse_selecting = False  # set mouse_selecting flag attribute as False
        self.game_music_playing = False  # set in game music as False (in game music OFF to start)

    def main_loop(self):
        play_menu_music()  # game starts in menu, ergo play menu music
        while True:
            game_events = self._input_handler()
            self._game_logic_and_music(game_events)
            render_display()

    def _input_handler(self):
        events = pg.event.get()  # define variable shortcut for pygame events

        # Close program via window
        for event in events:
            if event.type == pg.QUIT:
                exit_game()  # run exit_game from game_modes (terminates program)

            # Event handler if inside menu
            if self.in_menu:

                # When left mouse button is pressed (perform menu actions)
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # get index based on mouse click (logic handled in menu.py file)
                    mouse_action_index = menu.handle_mouse_click(event.pos)
                    if mouse_action_index is not None:
                        self.action_index = mouse_action_index  # the action index is whatever the mouse is clicking
                        self.mouse_selecting = True  # set mouse selecting flag as True (mouse is currently selecting)
                        # If action index based on mouse click == 0 (first in list)
                        if self.action_index == 0:  # start two player game mode
                            # print("'New Game' clicked.") // <- uncomment to help debug
                            reset_game()  # run reset_game from game_modes (resets in game parameters)
                            self.in_menu = False  # set in_menu flag attribute as False (NOT currently in menu)
                            self.in_game = True  # set in_game flag attribute as True (currently in game)
                            self.new_game_started = True  # new game was started

                        # Else if action index based on mouse click == 1 (second in list)
                        elif self.action_index == 1:
                            # print("'Quit' clicked.") // <- uncomment to help debug
                            exit_game()  # run exit_game from game_modes (terminates program)

                # When left mouse button is released (mouse is currently NOT selecting)
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.mouse_selecting = False  # set mouse_selecting attribute flag as False

                # Handle mouse hover to highlight menu selection
                elif event.type == pg.MOUSEMOTION:
                    # get index based on mouse position (logic handled in menu.py file)
                    mouse_action_index = menu.handle_mouse_click(event.pos)
                    # update the selected index based on mouse hover
                    if mouse_action_index is not None and not self.mouse_selecting:
                        self.action_index = mouse_action_index  # the action index is whatever the mouse is hovering

                        # print(self.action_index) // <- uncomment to help debug

                # Check if event KEY has been pressed down
                elif event.type == pg.KEYDOWN:
                    # ESCAPE KEY
                    if event.key == pg.K_ESCAPE:
                        # if ESC is pressed and currently in game
                        if self.in_game:
                            # Go back in menu
                            self.in_menu = True  # set in_menu flag attribute as True
                            self.in_game = False  # set in_game flag attribute as False
                            pause_game()  # run pause_game from game_modes (stops countdown sfx if <= 3 and reset it)
                        # if ESC is pressed, currently in menu and a new game was started at some point (is True)
                        elif self.in_menu and self.new_game_started:
                            # Jump back in game
                            self.in_menu = False  # set in_menu flag attribute as False
                            self.in_game = True  # set in_game flag attribute as True

                    # ENTER/RETURN KEY
                    elif event.key == pg.K_RETURN:
                        # if RETURN is pressed perform action based on its index
                        if self.action_index == 0:  # if index 0, start new game
                            # print("'New Game' selected.") // <- uncomment to help debug
                            self.in_menu = False  # set in_menu flag attribute as False (currently NOT in menu)
                            self.in_game = True  # set in_game flag attribute as True (currently in game)
                            self.new_game_started = True  # new game has been started
                            reset_game()  # run reset_game from game_modes (resets in game parameters)
                        elif self.action_index == 1:  # if index 1, quit game and terminate program
                            # print("'Quit' selected.") // <- uncomment to help debug
                            exit_game()  # run exit_game from game_modes (terminates program)

                    # UP KEY (ARROW)
                    elif event.key == pg.K_UP:  # navigate up the menu with UP arrow key
                        # check if mouse is not actively selecting to avoid conflict between mouse and keys
                        if not self.mouse_selecting:  # if mouse is not actively selecting
                            # traverse the length of the menu and substract one from the current action index
                            self.action_index = (self.action_index - 1) % len(menu.mastermenu_selections)
                    # DOWN KEY (ARROW)
                    elif event.key == pg.K_DOWN:  # Apply same logic to navigate down the menu with DOWN arrow key
                        if not self.mouse_selecting:
                            self.action_index = (self.action_index + 1) % len(menu.mastermenu_selections)

                # When a key is being pressed DOWN, update the menu selections color to higlight the selection
                # Default is WHITE
                menu.mastermenu_colors = [WHITE] * len(menu.mastermenu_selections)
                # The action index selected is SUNSET_ORANGE
                menu.mastermenu_colors[self.action_index] = SUNSET_ORANGE

            # Event handler if in game
            elif self.in_game:

                # Check if event KEY has been pressed down
                if event.type == pg.KEYDOWN:
                    # ESCAPE KEY
                    if event.key == pg.K_ESCAPE:
                        # Go back in menu
                        self.in_menu = True  # set in_menu flag attribute as True
                        self.in_game = False  # set in_game flag attribute as False
                        pause_game()  # run pause_game from game_modes (stops countdown sfx if <= 3 and reset it)

        return events

    def _game_logic_and_music(self, events):
        # If in_menu is True, display the master_menu instance of our MasterMenu class
        if self.in_menu:
            menu.display(window, events)
            # If game music playing (is True)
            if self.game_music_playing:
                pg.mixer.music.stop()  # first stop ongoing music
                self.game_music_playing = False  # set game_music_playing flag as False (game music NOT currently on)
                play_menu_music()  # start menu music

        # If in_game is True, run two_player_mode from game_modes (PvP/2Player standard match)
        elif self.in_game:
            two_player_mode()
            # If game music NOT playing (is False)
            if not self.game_music_playing:
                pg.mixer.music.stop()  # first stop ongoing music
                play_game_music()  # play game music
                self.game_music_playing = True  # set game_music_playing flag as True (game music currently on)
        # Else set game music back to initial/default state as Flase (NOT playing)
        else:
            self.game_music_playing = False
