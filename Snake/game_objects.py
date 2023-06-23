# Snake/game_objects.py
import pygame as pg
from random import randrange
from constants import WINDOW_SIZE, TILE_SIZE, BLACK, WINDOW_OFFSET
from images import snake_food
from sound import play_pickup_food_sound, play_crash_sound

vec2d = pg.math.Vector2  # save pygame class for working with 2D vectors into an easily accessible variable


def randomize_location(player):
    while True:
        # Use randrange function from random module to randomize x & y coordinates within the game area
        x = randrange(WINDOW_OFFSET + TILE_SIZE // 2, WINDOW_SIZE[0] - WINDOW_OFFSET - TILE_SIZE // 2, TILE_SIZE)
        y = randrange(WINDOW_OFFSET + TILE_SIZE // 2, WINDOW_SIZE[1] - WINDOW_OFFSET - TILE_SIZE // 2, TILE_SIZE)
        # Create a food rect with assigned coordinates with width and length of tile size
        food_rect = pg.Rect((x, y), (TILE_SIZE, TILE_SIZE))

        # Create variables that hold info on food rect, player head rect and player body rects location
        collides_with_player = player.rect.colliderect(food_rect)
        collides_with_body = any(body.colliderect(food_rect) for body in player.body_rects)

        # If the positions don't overlap, the new food location and the collision code is valid
        if not collides_with_player and not collides_with_body:
            return [x, y]


class Player:
    def __init__(self, game):
        self.game = game

        # Player head (main rect)
        self.rect = pg.rect.Rect([140 + 3 * TILE_SIZE, (WINDOW_SIZE[1] // 2 - TILE_SIZE), TILE_SIZE, TILE_SIZE])
        self.length = 1

        # Player body (all non-main rects)
        self.body_rects = []

        # Player directions
        self.direction = vec2d(TILE_SIZE, 0)  # initial starting direction: RIGHT (by increments of tile size)
        self.directions = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 0, pg.K_d: 1}  # possible initial directions (value: 1)

        # Player movement speed
        self.previous_move_time = 0  # variable to keep track of previous movement time
        self.move_delay = 100  # delay player movement by 0.1 sec

    def draw(self):
        # Draw player head rect
        head_rect = self.rect.inflate(-1, -1)  # deflate rect by 1px in width/length to not fully cover tile
        pg.draw.rect(self.game.window, BLACK, head_rect)

        # Draw rest of player body rects
        for body_rect in self.body_rects:
            body_rect = body_rect.inflate(-1, -1)
            pg.draw.rect(self.game.window, BLACK, body_rect)

    def delta_time(self):
        current_move_time = pg.time.get_ticks()  # get current move time in ms
        # Allow movement occurance when current time minus previous move time is greater than delay interval
        if current_move_time - self.previous_move_time > self.move_delay:
            self.previous_move_time = current_move_time  # save previous move time to current move time
            return True
        # Do NOT allow movement occurance in other instances
        return False

    def move(self):
        # If delta_time method returns True (required time interval has passed), allow movement occurance
        if self.delta_time():
            self.rect.move_ip(self.direction)  # move head rect in specific the direction using its vector as the arg
            self.body_rects.append(self.rect.copy())  # make copy of updated head rect and add to the list of body_rects

            # update body_rects list with current length amount counting from backwards to prevent indefinite growth
            self.body_rects = self.body_rects[-self.length:]

    def control(self, event):
        # Check for event key being pressed down
        if event.type == pg.KEYDOWN:
            # if key 'W' pressed and movement in that direction is possible
            if event.key == pg.K_w and self.directions[pg.K_w]:
                self.direction = vec2d(0, -TILE_SIZE)  # move UP by unit of tile size
                self.directions = {pg.K_w: 1, pg.K_s: 0, pg.K_a: 1, pg.K_d: 1}  # make movement downward NOT possible

            # if key 'S' pressed and movement in that direction is possible
            if event.key == pg.K_s and self.directions[pg.K_s]:
                self.direction = vec2d(0, TILE_SIZE)  # move DOWN by unit of tile size
                self.directions = {pg.K_w: 0, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}  # make movement upward NOT possible

            # if key 'A' pressed and movement in that direction is possible
            if event.key == pg.K_a and self.directions[pg.K_a]:
                self.direction = vec2d(-TILE_SIZE, 0)  # move LEFT by unit of tile size
                self.directions = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 0}  # make movement right NOT possible

            # if key 'D' pressed and movement in that direction is possible
            if event.key == pg.K_d and self.directions[pg.K_d]:
                self.direction = vec2d(TILE_SIZE, 0)  # move RIGHT by unit of tile size
                self.directions = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 0, pg.K_d: 1}  # make movement left NOT possible

    def food_collision(self):
        # If player head rect collides with food rect
        if self.rect.colliderect(self.game.food.rect):
            new_food_location = randomize_location(self)  # randomize a new location for food
            self.game.food.rect.center = new_food_location  # update food rect center coordinates w/ new location x & y
            self.length += 1  # add 1 to length counter when food is picked up
            play_pickup_food_sound()

        # Return the self.length counter variable
        return self.length

    def border_collision(self):
        # If player head rect collides with left or right side of the game area, end round
        if self.rect.left < 0 + WINDOW_OFFSET or self.rect.right > WINDOW_SIZE[0] - WINDOW_OFFSET:
            play_crash_sound()
            self.game.new_game()
            self.game.active = False
        # If player head rect collides with top or bottom side of the game area, end round
        if self.rect.top < 0 + WINDOW_OFFSET or self.rect.bottom > WINDOW_SIZE[1] - WINDOW_OFFSET:
            play_crash_sound()
            self.game.new_game()
            self.game.active = False

    def auto_collision(self):
        # If player head rect collides with itself (its body rects), end round
        if len(self.body_rects) != len(set(rect.center for rect in self.body_rects)):
            play_crash_sound()
            self.game.active = False
            self.game.new_game()

    def update(self):
        # If game is active, run the Player class methods below
        if self.game.active:
            self.move()
            self.food_collision()
            self.border_collision()
            self.auto_collision()


class Food:
    def __init__(self, game, player):
        self.game = game
        self.image = pg.image.load(snake_food)
        self.image = pg.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = randomize_location(player)  # randomize food rect location center coordinates at init

    def draw(self):
        # Draw food image using its rect on window
        self.game.window.blit(self.image, self.rect)
