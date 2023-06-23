# Snake/main.py
import sys
from game_objects import *
from constants import FPS, WATER_LEAF, PALE_BLUE_LILY, GREEN_SPRING_RAIN
from font import space_txt, score_txt
from images import snake_ico, trophy, musical_note
from sound import play_background_music
from highscore import load_highscore, save_highscore


class Game:
    def __init__(self):
        pg.init()
        self.window = pg.display.set_mode(WINDOW_SIZE)
        pg.display.set_caption("Snake | by Ilija")
        pg.display.set_icon(pg.image.load(snake_ico))
        self.clock = pg.time.Clock()
        self.player = None
        self.food = None
        self.active = False
        self.music_playing = True
        self.game_area_rect = pg.Rect(WINDOW_OFFSET, WINDOW_OFFSET,
                                      WINDOW_SIZE[0] - 2 * WINDOW_OFFSET, WINDOW_SIZE[1] - 2 * WINDOW_OFFSET)

        self.high_score = load_highscore()
        self.new_game()
        play_background_music()

    def new_game(self):
        # Create new instances of player and food every time new game is called
        self.player = Player(self)
        self.food = Food(self, self.player)

    def grid_background(self):
        # Create a grid background
        rows = WINDOW_SIZE[0] // TILE_SIZE
        columns = WINDOW_SIZE[1] // TILE_SIZE

        # Iterate for every row in range of rows and every column in range of columns
        for row in range(rows):
            for column in range(columns):
                tile_rect = pg.Rect((row * TILE_SIZE, column * TILE_SIZE),
                                    (TILE_SIZE, TILE_SIZE))

                # Alternate colors for every odd and even tile
                if (row + column) % 2 == 0:
                    pg.draw.rect(self.window, WATER_LEAF, tile_rect)
                else:
                    pg.draw.rect(self.window, PALE_BLUE_LILY, tile_rect)

    def solid_background(self):
        self.window.fill(GREEN_SPRING_RAIN)
        pg.draw.rect(self.window, BLACK, self.game_area_rect, 2)

    def music_switch(self):
        # Graphics for switching music on/off
        music_note_img = pg.image.load(musical_note)
        music_note_img = pg.transform.scale(music_note_img, (TILE_SIZE, TILE_SIZE))
        music_note_img_rect = music_note_img.get_rect(center=(WINDOW_SIZE[0] // 2 + 305, WINDOW_SIZE[1] // 2 - 240))

        if self.music_playing:
            self.window.blit(music_note_img, music_note_img_rect)

        music_switch_surface = score_txt.render("M : ", True, BLACK)
        music_switch_rect = music_switch_surface.get_rect(center=(WINDOW_SIZE[0] // 2 + 275, WINDOW_SIZE[1] // 2 - 239))
        self.window.blit(music_switch_surface, music_switch_rect)

    def start_msg(self):
        # Graphics for the space-to-start graphics at the bottom of the window
        if not self.active:
            space_text = space_txt.render("SPACE", True, BLACK)
            space_rect = space_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 260))
            rect_width = space_rect.width + 60
            rect_height = space_rect.height + 10
            rect = pg.Rect(
                space_rect.centerx - rect_width // 2, space_rect.centery - rect_height // 2 - 2, rect_width, rect_height
            )
            pg.draw.rect(self.window, BLACK, rect, 3)
            self.window.blit(space_text, space_rect)

    def scoreboard(self):
        # Graphics for the scoreboard
        score = self.player.length - 1
        score_img = pg.image.load(snake_food)
        score_img = pg.transform.scale(score_img, (TILE_SIZE, TILE_SIZE))
        score_img_rect = score_img.get_rect(center=(WINDOW_SIZE[0] // 2 - 300, WINDOW_SIZE[1] // 2 - 275))
        self.window.blit(score_img, score_img_rect)

        score_surface = score_txt.render(str(score), True, BLACK)
        score_rect = score_surface.get_rect(center=(WINDOW_SIZE[0] // 2 - 265, WINDOW_SIZE[1] // 2 - 274))
        self.window.blit(score_surface, score_rect)

    def highscore(self):
        # Graphics for the highscore
        highscore_img = pg.image.load(trophy)
        highscore_img = pg.transform.scale(highscore_img, (TILE_SIZE, TILE_SIZE))
        highscore_img_rect = highscore_img.get_rect(center=(WINDOW_SIZE[0] // 2 - 300, WINDOW_SIZE[1] // 2 - 240))
        self.window.blit(highscore_img, highscore_img_rect)

        highscore_surface = score_txt.render(str(self.high_score), True, BLACK)
        highscore_rect = highscore_surface.get_rect(center=(WINDOW_SIZE[0] // 2 - 265, WINDOW_SIZE[1] // 2 - 239))
        self.window.blit(highscore_surface, highscore_rect)

    def draw(self):
        self.solid_background()
        self.start_msg()
        self.scoreboard()
        self.highscore()
        self.music_switch()
        self.player.draw()
        if self.active:
            self.food.draw()

    def event_handler(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Player controls
            self.player.control(event)

            # Check for event key being pressed down
            if event.type == pg.KEYDOWN:
                # 'SPACE' key press to start the game
                if event.key == pg.K_SPACE:
                    if not self.active:
                        self.active = True

                # 'M' key to toggle in game music
                elif event.key == pg.K_m:
                    self.toggle_music()

    def play_music(self):
        if self.music_playing and not pg.mixer.music.get_busy():
            play_background_music()

    def toggle_music(self):
        self.music_playing = not self.music_playing

        if self.music_playing:
            pg.mixer.music.unpause()
        else:
            pg.mixer.music.pause()

    def update(self):
        # Update highscore dynamically while in game
        if self.player.length - 1 > self.high_score:
            self.high_score = self.player.length - 1
            save_highscore(self.high_score)

        self.player.update()
        pg.display.flip()
        self.clock.tick(FPS)

    def run(self):
        while True:
            self.event_handler()
            self.draw()
            self.play_music()
            self.update()
