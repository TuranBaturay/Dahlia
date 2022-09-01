from .mode import Mode
import gui as gui
import lib as lib
import pygame
from pygame.locals import *


class Settings(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.track = 0
        self.toggle_music.toggle(False)
        self.dim_surf = pygame.Surface((lib.WIDTH, lib.HEIGHT))
        self.dim_surf.set_alpha(70)

    def init_gui(self):
        settings_panel = gui.Panel(
            self.gui_list,
            50,
            50,
            lib.WIDTH - 100,
            lib.HEIGHT - 100,
            color=lib.dark_blue,
            border_radius=10,
        )

        title = gui.TextBox(
            self.gui_list,
            settings_panel.rect.x,
            settings_panel.rect.y,
            settings_panel.rect.w,
            30,
            text="Settings",
            color=lib.wet_blue,
            border_radius=10,
        )
        gui.Button(
            self.gui_list,
            *title.rect.topleft,
            60,
            30,
            text="<",
            align="center",
            func=lambda: self.app.set_mode(self.app.previous_mode),
            color=lib.wet_blue,
            border_radius=10,
        )

        box = gui.Panel(
            self.gui_list,
            settings_panel.rect.x + 50,
            settings_panel.rect.y + 50,
            600,
            400,
            color=lib.wet_blue,
        )
        label = gui.TextBox(
            self.gui_list,
            *box.rect.topleft,
            box.rect.w,
            30,
            text="Music",
            align="left",
            color=lib.wet_blue,
        )
        self.toggle_music = gui.Toggle(
            self.gui_list,
            box.rect.x,
            label.rect.bottom,
            160,
            40,
            "OFF",
            func=lambda x: [
                self.volume_slider.set_value(x),
                self.toggle_music.set_text("ON" if x else "OFF"),
            ],
            color=lib.wet_blue,
        )
        gui.Button(
            self.gui_list,
            self.toggle_music.rect.right,
            self.toggle_music.rect.top,
            20,
            40,
            text="<",
            func=self.prev_track,
            color=lib.wet_blue,
        )
        gui.Button(
            self.gui_list,
            self.toggle_music.rect.right + 20,
            self.toggle_music.rect.top,
            20,
            40,
            text=">",
            func=self.next_track,
            color=lib.wet_blue,
        )
        self.volume_slider = gui.Slider(
            self.gui_list,
            self.toggle_music.rect.right + 40,
            label.rect.bottom,
            200,
            40,
            "Volume",
            self.set_volume,
            color=lib.wet_blue,
        )
        fullscreen_button = gui.Toggle(
            self.gui_list,
            box.rect.x,
            self.toggle_music.rect.bottom + 30,
            200,
            40,
            text="FULLSCREEN",
            func=lambda x: [
                pygame.display.toggle_fullscreen(),
            ],
            color=lib.wet_blue,
        )
        gui.Button(
            self.gui_list,
            settings_panel.rect.x + 20,
            settings_panel.rect.bottom - 60,
            130,
            40,
            "Back to Title",
            func=lambda: self.app.set_mode("title"),
            color=lib.wet_blue,
        )

    def next_track(self):
        self.track += 1
        if self.track >= len(self.app.musics):
            self.track = 0
        self.set_track(self.track)

    def prev_track(self):
        self.track -= 1
        if self.track < 0:
            self.track = len(self.app.musics) - 1
        self.set_track(self.track)

    def set_track(self, track):
        if not self.app.bgm_channel.get_busy():
            self.toggle_music.toggle(True)
        key_list = list(self.app.musics.keys())

        if type(track) is int:
            if track < 0 or track >= len(self.app.musics):
                return
            self.track = track
            track = key_list[track]
        else:
            if not track in self.app.musics.keys():
                return
            self.track = key_list.index(track)
            # print(self.track)

        if self.app.bgm_channel.get_sound() != self.app.musics[track]:
            self.app.bgm_channel.play(self.app.musics[track], loops=-1)
            self.current_track = track

    def set_volume(self, value):
        self.app.music_set_volume(value)
        if value > 0:
            if not self.toggle_music.get():
                self.toggle_music.toggle(True, callback=False)
                self.toggle_music.set_text("ON")
        else:
            if self.toggle_music.value:
                self.toggle_music.toggle(False, callback=False)
                self.toggle_music.set_text("OFF")

    def onkeydown(self, key, caps=None):
        if key == K_ESCAPE:
            self.app.set_mode(self.app.previous_mode)

    def update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp, (0, 0))
        self.display.blit(self.dim_surf, (0, 0))
        return super().update(dt, mouse, mouse_button, mouse_pressed)
