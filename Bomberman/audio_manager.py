# Ilijablaster/audio_manager.py
import pygame as pg
from settings import join, BASE_AUDIO_DIR


class AudioManager:
    def __init__(self, game):
        # REFERENCE
        self.game = game

        # MIXER SETTINGS
        pg.mixer.pre_init(frequency=48000, size=32, channels=2, buffer=512)
        pg.mixer.init(frequency=48000, size=-16, channels=2, buffer=1024)
        self.num_of_channels = 8
        self.channels = [pg.mixer.Channel(i) for i in range(self.num_of_channels)]

        # SOUNDEFFECTS FILE PATHS
        self.sound_effect_paths = {
            'menu_nav': join(BASE_AUDIO_DIR, 'menu_nav_sfx.ogg'),
            'menu_confirm': join(BASE_AUDIO_DIR, 'menu_confirm_sfx.ogg'),
            'menu_adjust': join(BASE_AUDIO_DIR, 'menu_adjust_sfx.ogg'),
            'end_game_victory': join(BASE_AUDIO_DIR, 'end_game_victory_sfx.ogg'),
            'end_game_defeat': join(BASE_AUDIO_DIR, 'end_game_defeat_sfx.ogg'),
            'pause_game': join(BASE_AUDIO_DIR, 'pause_game_sfx.ogg'),
            'exit_portal_reveal': join(BASE_AUDIO_DIR, 'exit_portal_reveal_sfx.ogg'),
            'powerup_reveal': join(BASE_AUDIO_DIR, 'powerup_reveal_sfx.ogg'),
            'powerup_pickup': join(BASE_AUDIO_DIR, 'powerup_pickup_sfx.ogg'),
            'bomb_countdown_tick': join(BASE_AUDIO_DIR, 'bomb_countdown_tick_sfx.ogg'),
            'bomb_explosion': join(BASE_AUDIO_DIR, 'bomb_explosion_sfx.ogg'),
            'player_death': join(BASE_AUDIO_DIR, 'player_death_sfx.ogg')
        }

        # SOUNDTRACK FILE PATHS
        self.soundtrack_paths = {
            'menu': join(BASE_AUDIO_DIR, 'menu_theme_track.wav'),
            'ingame': join(BASE_AUDIO_DIR, 'game_theme_track.wav')
        }

        # SOUNDEFFECTS
        self.sound_effects = {name: pg.mixer.Sound(path) for name, path in self.sound_effect_paths.items()}

        # SFX FLAGS
        self.sound_effects_enabled = True
        self.victory_sfx_playing = False
        self.defeat_sfx_playing = False

        # MUSIC
        self.soundtracks = {track: path for track, path in self.soundtrack_paths.items()}

        # MUSIC FLAGS
        self.menu_soundtrack_playing = False
        self.ingame_soundtrack_playing = False

    # This function toggles the game's soundeffects ON/OFF based on what is selected in menu audio options
    def toggle_sfx(self):
        if self.game.menu.in_audio:
            self.sound_effects_enabled = 'ON' in self.game.menu.audio_options[1]

    # This function adjust the game's music volume based on what is selected in menu audio options
    def adjust_music_volume(self):
        # If str 'OFF' found at index 0 in audio options set music volume to 0 (mute music)
        if 'OFF' in self.game.menu.audio_options[0]:
            pg.mixer.music.set_volume(0)
        # Else, set music volume based on the percentage number inside the str
        else:
            new_volume_percentage = int(self.game.menu.audio_options[0].split()[-2].strip('<>%'))
            pg.mixer.music.set_volume(new_volume_percentage / 100)

    # This function plays a sound effect based on the provided effect name and volume.
    def play_sfx(self, effect_name, volume=1.0):
        effect_sound = self.sound_effects.get(effect_name)
        if effect_sound:
            effect_sound.set_volume(volume if self.sound_effects_enabled else 0)
            effect_sound.play(maxtime=0)

    # This function stops all currently playing sound effects
    def stop_all_sfx(self):
        for sound_effect in self.sound_effects.values():
            sound_effect.stop()

    # This function plays the menu sountrack
    def play_menu_track(self):
        pg.mixer.music.load(self.soundtracks['menu'])
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(1)

    # This function plays the ingame sountrack
    def play_ingame_track(self):
        pg.mixer.music.load(self.soundtracks['ingame'])
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(1)

    # This function handles the soundtrack arrangement (what track is played at what condition) for the game
    def track_arrangement(self):
        if self.game.in_menu:
            if not self.menu_soundtrack_playing:
                self.play_menu_track()
                self.menu_soundtrack_playing = True
                self.ingame_soundtrack_playing = False
        else:
            if not self.ingame_soundtrack_playing:
                self.play_ingame_track()
                self.ingame_soundtrack_playing = True
                self.menu_soundtrack_playing = False

            # Mute pygame mixer music when player collides with creep or is hit by bomb explosion
            for player in self.game.players:
                if player.collided_with_creep or player.hit_by_bomb_explosion or player.collided_with_exit_portal:
                    pg.mixer.music.set_volume(0)

            # Mute pygame mixer music when game is paused or end game screen is pulled up
            if self.game.menu.in_end or self.game.paused:
                pg.mixer.music.set_volume(0)

    # This function handles dynamic updates for the audio
    def update(self):
        self.toggle_sfx()
        self.adjust_music_volume()
        self.track_arrangement()
