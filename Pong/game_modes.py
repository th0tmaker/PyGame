import sys
from constants import WINDOW_SIZE, PADDLE_SIZE, LIMED_SPRUCE
from setup import pg, access_window
from sound import countdown321_sfx
from player_paddle import left_paddle, right_paddle, paddle_list
from ball import ball

window = access_window()  # access game window


# PvP/2-Player Game Mode
def two_player_mode():
    window.fill(LIMED_SPRUCE)  # Draw and update background

    for paddle in paddle_list:
        paddle.draw(window)  # Draw paddles
        paddle.run()  # Update paddles

    ball.draw()  # draw ball
    ball.run()  # run ball code

    pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)  # set program cursor to default (ARROW) when in game


# Reset game to initial state
def reset_game():
    ball.round_reset(ball.left_paddle_score, ball.right_paddle_score, paddle_list)  # Reset round parameters

    ball.left_paddle_score = 0  # Reset left paddle score
    ball.right_paddle_score = 0  # Reset right paddle score

    # Update left paddle x, y coordinates and rect position
    left_paddle.x, left_paddle.y = 20, (WINDOW_SIZE[1] // 2 - PADDLE_SIZE[1] // 2)  # coordinates
    left_paddle.rect.topleft = (left_paddle.x, left_paddle.y)  # rect to coordinates position

    # Update right paddle x, y coordinates and rect position
    right_paddle.x, right_paddle.y = (WINDOW_SIZE[0] - 20 - PADDLE_SIZE[0]), \
                                     (WINDOW_SIZE[1] // 2 - PADDLE_SIZE[1] // 2)
    right_paddle.rect.topleft = (right_paddle.x, right_paddle.y)


# If ESC key is pressed during countdown, restart timer back to start
def pause_game():
    elapsed_duration = pg.time.get_ticks() - ball.round_start_time  # calculate elapsed duration
    if elapsed_duration <= 10000:  # check if elapsed duration is less than or equal to 10 seconds

        # Set timer parameters back to initial state
        ball.round_start_timer_duration = 10000
        ball.round_start_time = 0
        ball.start_timer_active = False
        ball.ball_active = False

    countdown321_sfx.stop()  # prevent countdown sfx from continuing to play


# Function to easily handle exiting the program
def exit_game():
    pg.quit()
    sys.exit()
