# Ilijablaster/level_manager.py
import random


class LevelManager:
    def __init__(self, game, level_matrix):
        # REFERENCE
        self.game = game  # Reference to the Game class to access its attributes & methods

        # LEVEL (Define the original state of the level and make a deep working copy of it for further modifications)
        self.level_matrix_initial_state = level_matrix  # Store the initial state of the level matrix
        self.level_matrix = [row[:] for row in self.level_matrix_initial_state]  # Deep copy

    # This function labels the positions inside the level matrix where the player/s in game will start
    def label_player_starting_cell(self, row_index, col_index):
        # Check if the indices are within the bounds of the matrix
        if 0 <= row_index < len(self.level_matrix) and 0 <= col_index < len(self.level_matrix[0]):
            self.level_matrix[row_index][col_index] = 3  # assign value to '3' ('3'=PLAYER STARTING POSITION)

    # This function labels the position inside the level matrix ajacent to the player/s starting position
    def label_player_adjacent_cells(self):
        # Define the directions to check for adjacent cells (left, right, up, down)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Iterate through the game map to find player starting position (assigned value '3')
        for row in range(len(self.level_matrix)):
            for col in range(len(self.level_matrix[row])):
                # Check if cell value is '3'
                if self.level_matrix[row][col] == 3:
                    # Check adjacent cells in each direction
                    for x_direction, y_direction in directions:
                        new_row, new_col = row + x_direction, col + y_direction
                        # Check if the adjacent cell is within bounds and has a clear cell (value '1')
                        if 0 <= new_row < len(self.level_matrix) and 0 <= new_col < len(self.level_matrix[row]) \
                                and self.level_matrix[new_row][new_col] == 1:
                            self.level_matrix[new_row][new_col] = 4  # set value to '4' ('4'=PLAYER ADJACENT POSITION)

        # Return the updates to the self.level_matrix
        return self.level_matrix

    # This function iterates through cells inside the matrix level and selects viable spawn cells for brittle objects
    def select_viable_brittle_cells(self, num_of_brittles):
        # Define a list for valid brittle cells (only cells that have value '1' in level matrix are valid)
        valid_brittle_cell_positions = []

        # Iterate through the level matrix rows and columns
        for row in range(len(self.level_matrix)):
            for col in range(len(self.level_matrix[row])):
                # Check if cell value is path ('1')
                if self.level_matrix[row][col] == 1:
                    # Check if adjacent cells of path (value '1') are NOT player starting pos (value '3')
                    # This prevents brittle objects from being placed at player starting position
                    if all(self.level_matrix[row + x][col + y] not in {3}
                           for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                        valid_brittle_cell_positions.append((row, col))

        # Randomly populate specified number of cells with brittle objects
        brittle_cells = random.sample(valid_brittle_cell_positions, num_of_brittles)

        # Update the level matrix to represent 'brittles' at the selected positions
        for row, col in brittle_cells:
            self.level_matrix[row][col] = 5  # assign value to '5' ('5'=BRITTLE)

        # Return the updates to the self.level_matrix
        return self.level_matrix

    # This function iterates through cells inside the matrix level and selects viable spawn cells for brittle objects
    def select_exit_portal_location_cell(self):
        # Get all available brittle cells to select as potential locations for the exit portal
        valid_exit_portal_cells = [(row, col) for row in range(len(self.level_matrix))
                                   for col in range(len(self.level_matrix[row])) if
                                   self.level_matrix[row][col] == 5]

        # If there are available brittle cells
        if valid_exit_portal_cells:
            exit_portal = random.choice(valid_exit_portal_cells)  # randomly select one to set as exit portal cell
            row, col = exit_portal
            self.level_matrix[row][col] = 7  # assign value to '7' ('7'=EXIT_PORTAL(BR))
        else:
            # In case of no available brittle cells
            print("No location found for exit portal. Number of brittle objects:", len(valid_exit_portal_cells))

        # Return the updates to the self.level_matrix
        return self.level_matrix

    # This function handles the level setup
    def setup(self):
        # Label the starting cell for players based on the game mode
        if self.game.game_mode_1player:
            self.label_player_starting_cell(1, 1)  # player 1 starting cell
        elif self.game.game_mode_2player:
            self.label_player_starting_cell(1, 1)  # player 1 starting cell
            self.label_player_starting_cell(11, 27)  # player 2 starting cell

        # Label the cells adjacent to the players starting positions
        self.label_player_adjacent_cells()

        # Determine the number of brittle objects based on the selected custom options
        if 'Default' in self.game.menu.custom_options[0]:
            self.select_viable_brittle_cells(num_of_brittles=75)  # default num of brittles (hardcoded)
        elif 'Custom' in self.game.menu.custom_options[0]:
            num_of_brittles_key_str = self.game.menu.custom_options[1].split('<')[-1].split('>')[0].strip()
            custom_num_of_brittles = int(num_of_brittles_key_str)
            self.select_viable_brittle_cells(
                num_of_brittles=custom_num_of_brittles)  # custom num of brittles (custom options)

        # Select the location of the exit portal
        self.select_exit_portal_location_cell()

    # This function resets the level back to its initial state before the function-based modifications
    def reset(self):
        self.level_matrix = [row[:] for row in self.level_matrix_initial_state]
