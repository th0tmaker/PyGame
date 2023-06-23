# Snake/highscore.py
import os

HIGHSCORE_FILE = "highscore.txt"


# Function that handles loading highscore into the game
def load_highscore():
    # If path of our highscore file exists (is True)
    if os.path.exists(HIGHSCORE_FILE):
        # Open highscore file in read-mode (if there is no value found, return 0)
        with open(HIGHSCORE_FILE, "r") as file:
            try:
                high_score = int(file.read())  # save the contents of file being read into high_score as int
                return high_score
            except ValueError:
                return 0
    else:
        return 0


# Function that handles saving the highscore
def save_highscore(score):
    # Store whatever the load_highscore function returns into a variable called current_highscore
    current_highscore = load_highscore()
    # If the provided argument for score is greater than current_highscore
    if score > current_highscore:
        # Overwrite highscore file contents with score value
        with open(HIGHSCORE_FILE, "w") as file:
            file.write(str(score))
