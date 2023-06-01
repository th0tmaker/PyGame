# Pong/ball.py
import time
import random
from constants import WINDOW_SIZE, LIMED_SPRUCE, WHITE, SUNSET_ORANGE
from setup import pg, access_window
from font import countdown321_txt, score_txt
from sound import play_countdown321_sound, play_paddle_strike_sound, play_point_scored_sound
from player_paddle import paddle_list

window = access_window()  # access game window


# Drawing the game score
def display_game_score(surface, left_paddle_score, right_paddle_score):
    left_paddle_score_txt = score_txt.render(str(left_paddle_score), True, WHITE)
    right_paddle_score_txt = score_txt.render(str(right_paddle_score), True, WHITE)

    left_score_pos = (ball.x - ball.radius - 200 - left_paddle_score_txt.get_width(), 20)
    right_score_pos = (ball.x + ball.radius + 200, 20)

    surface.blit(left_paddle_score_txt, left_score_pos)
    surface.blit(right_paddle_score_txt, right_score_pos)


# Create a class that will handle the general code for the game ball
class Ball:
    def __init__(self, x, y, radius, velocity_x, velocity_y, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.rect = pg.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color

        self.left_paddle_score = 0
        self.right_paddle_score = 0

        self.paddle_collisions = 0  # initialize counter to track every time ball collides w/ a paddle
        self.last_time_collided = 0  # initialize flag to track time at which last collision occured
        self.y_velocity_cap = 4  # maximum speed at the ball can travel in its y direction

        self.round_start_time = 0  # initialize flag to track when the round has started
        self.round_start_timer_duration = 10000  # Countdown timer duration is 10000ms (10 sec)

        self.ball_active = False  # set ball_active flag attribute as False (not active by default)
        self.start_timer_active = False  # set start_timer_active flag attribute as False (not active by default)

        self.countdown_sfx_playing = False  # # set countdown_sfx flag attribute as False (not playing by default)

    def draw(self):
        # Define parameters to draw ball
        pg.draw.circle(surface=window, color=self.color, center=(self.x, self.y), radius=self.radius)

    def move(self):
        # Update the x and y position of the ball by incrementing its x and y velocity
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Update ball rect center position based on its x and y coordinates
        self.rect.center = (self.x, self.y)

    def out_of_bounds(self):
        # Change ball y direction by its y velocity when ball collides with top of the window
        if self.rect.top <= 0:
            self.rect.top = 1  # insurance to prevent the ball from being stuck on top wall
            self.velocity_y = abs(self.velocity_y)  # change y direction

        # Change ball y direction by its y velocity when ball collides with bottom of the window
        elif self.rect.bottom >= WINDOW_SIZE[1]:
            self.rect.bottom = WINDOW_SIZE[1] - 1  # insurance to prevent the ball from being stuck on bottom wall
            self.velocity_y = -abs(self.velocity_y)  # change y direction

    def start_round_countdown(self):
        # Countdown timer before each round starts to get the players ready
        current_time = pg.time.get_ticks()  # get current time
        elapsed_time = current_time - self.round_start_time  # calc how much time elapsed from start of round to now

        # If elapsed time is greater or equal to the round start timer duration (currently set as: 10 sec)
        if elapsed_time >= self.round_start_timer_duration:
            self.ball_active = True  # set ball active as True
            self.start_timer_active = False  # set start timer active as False
            self.countdown_sfx_playing = False  # set countdown_sfx_playing as False

        # Else define countdown number and draw it on the window
        else:
            # Initialize countdown integer based on start timer duration minus elapsed time (divide by 1000 to get sec)
            countdown321_num = int((self.round_start_timer_duration - elapsed_time) / 1000) + 1

            # Render countdown text and create a rectangle for easier manipulation
            start_countdown = countdown321_txt.render(str(countdown321_num), True, WHITE)
            start_countdown_rect = start_countdown.get_rect(center=(WINDOW_SIZE[0] / 2 + 1, WINDOW_SIZE[1] / 2 + 75))

            # Draw countdown timer on screen
            pg.draw.rect(window, LIMED_SPRUCE, start_countdown_rect)
            window.blit(start_countdown, start_countdown_rect)

            # Play the countdown sound effect when timer is at 3 seconds or less
            if countdown321_num <= 3 and not self.countdown_sfx_playing:
                play_countdown321_sound()  # play countdown sound effect
                self.countdown_sfx_playing = True  # Set countdown_sound_playing flag as True

            self.ball_active = True  # set ball active as True after countdown expires

        # Run outer scope func to display game score(made intenionally visible ONLY when countdown is running)
        display_game_score(window, ball.left_paddle_score, ball.right_paddle_score)

    def round_reset(self, left_paddle_score, right_paddle_score, paddles):
        # Reset game parameters back to initial state
        self.x = WINDOW_SIZE[0] // 2  # reset ball.x position at the middle of the window
        self.y = WINDOW_SIZE[1] // 2  # reset ball.y position at the middle of the window
        self.rect.center = (self.x, self.y)  # reset ball rect center to x and y coordinates
        self.paddle_collisions = 0  # reset counter for every time ball collides w/ a paddle
        self.velocity_x = 3  # reset ball x velocity to inital state (currently set: 0.3)
        self.velocity_y = random.choice(
            (0.01, -0.01))  # reset ball y velocity to initial state but randomize trajectory
        self.ball_active = False  # set ball active as False

        for paddle in paddles:
            paddle.velocity = 600  # set paddle vertical velocity of to initial state (currently set: 600)

        # Determine ball direction at the start of the round
        if left_paddle_score == 0 and right_paddle_score == 0:
            self.velocity_x *= -1  # at start of round 1, left paddle gets the ball first every time
        elif left_paddle_score == right_paddle_score != 0:
            self.velocity_x *= random.choice([-1, 1])  # if game is tied, random paddle gets the ball
        elif right_paddle_score > left_paddle_score:
            self.velocity_x *= -1  # if right paddle is behind, right paddle gets the ball
        # Note: in every other scenario, left paddle gets the ball

        self.round_start_time = pg.time.get_ticks()  # initialize new start timer once the round starts
        self.start_timer_active = True  # set start timer as True

    def score_point(self):
        # Left paddle scores point (ball went off the screen to the right)
        if self.rect.left >= WINDOW_SIZE[0]:
            play_point_scored_sound()  # play point scored sound effect
            self.left_paddle_score += 1  # left paddle gets 1 point
            self.ball_active = False  # set ball active as False
            self.round_reset(self.left_paddle_score, self.right_paddle_score, paddle_list)  # reset round

            # print("left paddle score:", self.left_paddle_score) <- // for debugging

        # Right paddle scores point (ball went off the screen to the left)
        elif self.rect.right <= 0:
            play_point_scored_sound()  # play point scored sound effect
            self.right_paddle_score += 1  # right paddle gets 1 point
            self.ball_active = False  # set ball active as False

            self.round_reset(self.left_paddle_score, self.right_paddle_score, paddle_list)  # reset round

            # print("right paddle score:", self.right_paddle_score) <- // for debugging

    def ball_paddle_collision(self, paddles):
        # Main game logic that handles how the ball and paddle interact when they collide
        for paddle in paddles:
            # If ball rect and paddle rect collide with each other
            if self.rect.colliderect(paddle.rect):
                paddle_centery = paddle.rect.centery  # get paddle rect center y coordinate

                # If ball has collided with the left edge of the paddle (for RIGHT paddle)
                if self.rect.centerx < paddle.rect.left:
                    # reverse x (horizontal) direction
                    self.velocity_x = -abs(self.velocity_x)  # NOTE: reverse from positive value to negative value

                    # If bottom edge of ball rect >= the top edge of paddle rect
                    # And if top edge of ball rect is <= the bottom edge of paddle rect
                    if self.rect.bottom >= paddle.rect.top and self.rect.top <= paddle.rect.bottom:
                        # Calc distance from center substracting paddle center y from ball center y
                        distance_from_center = self.rect.centery - paddle_centery  # vertical distance from center
                        max_distance = paddle.rect.height / 2 + self.radius  # define max distance
                        # Calc velocit of y using linear interpolation formula
                        self.velocity_y = distance_from_center / max_distance * self.y_velocity_cap + \
                            random.uniform(-0.1, 0.1)  # add small randomness to avoid getting same (pos and neg) value

                # If ball has collided with the right edge of the paddle (for LEFT paddle)
                elif self.rect.centerx > paddle.rect.right:
                    # reverse x (horizontal) direction
                    self.velocity_x = abs(self.velocity_x)  # NOTE: reverse from negative value to positive value

                    # Same bounce logic as with right paddle
                    if self.rect.bottom >= paddle.rect.top and self.rect.top <= paddle.rect.bottom:
                        distance_from_center = self.rect.centery - paddle_centery
                        max_distance = paddle.rect.height / 2 + self.radius
                        self.velocity_y = distance_from_center / max_distance * self.y_velocity_cap + \
                            random.uniform(-0.1, 0.1)

                # Ball collided with top or bottom of paddle rect
                else:
                    # Calculate new values for paddle top and bottom side of paddle by accounting for ball size
                    paddle_top = paddle.rect.top - self.radius
                    paddle_bottom = paddle.rect.bottom + self.radius

                    # If bottom of ball is touching top of paddle and top of ball is touching bottom of paddle
                    if self.rect.bottom >= paddle_top and self.rect.top <= paddle_bottom:
                        self.velocity_y *= -1  # invert the oncoming y direction

                # Track when ball has collided with a paddle
                current_time = time.time()
                # Create a check to prevent multiple collisions occuring in quick succession by adding a delay
                if current_time - self.last_time_collided >= 0.5:
                    self.paddle_collisions += 1  # increment paddle_collisions counter
                    self.last_time_collided = current_time  # update the last collision time
                    play_paddle_strike_sound()  # play paddle strike sound effect

                # Every 10 paddle collisions, increase ball x velocity add a scaling difficulty to the gameplay
                if self.paddle_collisions % 10 == 0:
                    # calculate new x velocity value with sign preservation
                    delta_velocity = 1 * (1 if self.velocity_x > 0 else -1)
                    self.velocity_x += delta_velocity  # increase x velocity by 1 point

                # break out of loop since we only need to handle one collision per frame
                break

        # When ball collides with paddle a certain amount of times (threshold), increase the paddle movement velocity
        # (key = threshold of collisions, value = new paddle velocity)
        threshold_and_paddle_vel = {50: 800, 80: 1000}

        # loop through the threshold values in descending order
        for threshold in sorted(threshold_and_paddle_vel.keys(), reverse=True):
            # check if the number of paddle collisions exceeds the current threshold
            if self.paddle_collisions >= threshold:
                # set the paddles velocity to the corresponding value in the dictionary
                for paddle in paddles:
                    paddle.velocity = threshold_and_paddle_vel[threshold]
                # exit the loop to prevent setting the paddle velocity to a lower value
                break

        # // for debugging
        # for paddle in paddles:
        #    print(paddle.velocity)
        # print("pad collisions:", self.paddle_collisions)
        # print("x_vel:", round(self.velocity_x, 2), "y_vel:", round(self.velocity_y, 2))

    # Run function is responsible for running, refreshing, updating the ball code
    def run(self):
        if self.start_timer_active:
            self.start_round_countdown()
        elif self.ball_active:
            self.move()
            self.out_of_bounds()
            self.ball_paddle_collision(paddle_list)
            self.score_point()
        else:
            self.round_reset(self.left_paddle_score, self.right_paddle_score, paddle_list)


# Create instance of Ball class for the game ball
ball = Ball(x=(WINDOW_SIZE[0] // 2), y=(WINDOW_SIZE[1] // 2), radius=15,
            velocity_x=3, velocity_y=3, color=SUNSET_ORANGE)
