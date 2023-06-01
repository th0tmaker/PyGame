# Pong/player_paddle.py
import time
import pygame as pg
from constants import WINDOW_SIZE, PADDLE_SIZE, WHITE


# Create a class that will handle the general code for the player paddles
class PlayerPaddle:
    def __init__(self, x, y, width, height, velocity, color, up_key, down_key):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.velocity = velocity
        self.color = color
        self.up_key = up_key
        self.down_key = down_key
        self.movement = 0
        self.last_update_time = time.monotonic()

    # Draw paddles on window
    def draw(self, surface):
        pg.draw.rect(surface=surface, color=self.color, rect=self.rect)

    # Define paddle movement in game
    def paddle_movement(self):
        keys = pg.key.get_pressed()
        elapsed_time = time.monotonic() - self.last_update_time
        self.movement = (keys[self.down_key] - keys[self.up_key]) * self.velocity * elapsed_time
        self.rect.y += self.movement

    # Prevent paddle from moving out of bounds in any vertical direction
    def paddle_off_bounds(self):
        self.rect.top = max(self.rect.top, 0)  # paddle's top rect maximum value is 0
        self.rect.bottom = min(self.rect.bottom, WINDOW_SIZE[1])  # paddle's bottom rect maximum value is window height

    # Run function is responsible for running, refreshing, updating the paddle code
    def run(self):
        self.paddle_movement()
        self.paddle_off_bounds()
        self.last_update_time = time.monotonic()


# Create instance of PlayerPaddle class for the left paddle player
left_paddle = PlayerPaddle(x=20,
                           y=(WINDOW_SIZE[1] // 2 - PADDLE_SIZE[1] // 2),
                           width=PADDLE_SIZE[0],
                           height=PADDLE_SIZE[1],
                           velocity=600,
                           color=WHITE,
                           up_key=pg.K_w,
                           down_key=pg.K_s)

# Create instance of PlayerPaddle class for the right paddle player
right_paddle = PlayerPaddle(x=(WINDOW_SIZE[0] - 20 - PADDLE_SIZE[0]),
                            y=(WINDOW_SIZE[1] // 2 - PADDLE_SIZE[1] // 2),
                            width=PADDLE_SIZE[0],
                            height=PADDLE_SIZE[1],
                            velocity=600,
                            color=WHITE,
                            up_key=pg.K_o,
                            down_key=pg.K_l)

# Create paddle list to handle paddle related events together
paddle_list = [left_paddle, right_paddle]
