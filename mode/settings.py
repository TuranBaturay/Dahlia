
from .mode import Mode
import gui as gui
import lib as lib
import pygame
from pygame.locals import *
from pygame import BLEND_SUB


class Settings(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.track = 0
        self.toggle_music.toggle(False)
        self.dim_surf = pygame.Surface((lib.WIDTH, lib.HEIGHT))
        self.dim_surf.fill((20,20,20))
        #self.dim_surf.set_alpha(70)

    def init_gui(self):
        label_color = lib.dark_blue
        main_panel = gui.Panel(
            self.gui_list,
            50,
            50,
            lib.WIDTH - 100,
            lib.HEIGHT - 100,
            color=lib.dark_blue,
            border_radius=10
        )
        title_label = gui.TextBox(
            self.gui_list,
            main_panel.rect.x,
            main_panel.rect.y,
            main_panel.rect.w,
            30,
            text="Settings",
            color=lib.wet_blue,
            border_radius=10,
        )
        gui.Button(self.gui_list,
            *title_label.rect.topleft,
            30,30,"<",func=lambda : self.app.set_mode(self.app.previous_mode),
            color=lib.wet_blue,border_radius=10
        )
        left_panel = gui.Panel(
            self.gui_list,
            *title_label.rect.move(10,10).bottomleft,
            main_panel.rect.w //2 -20,main_panel.rect.h -20 - title_label.rect.h,
            color=lib.transparent,border=3,border_color=lib.wet_blue,border_radius=10
        )

        audio_control = gui.Panel(
            self.gui_list,
            *left_panel.rect.move(10,10).topleft,
            left_panel.rect.w -20,80,border=3,
            border_color=lib.wet_blue,border_radius=10
        )
        audio_label = gui.TextBox(
            self.gui_list,
            *audio_control.rect.topleft,
            100,30,text = "Audio",border_radius=10,color=label_color
        )

        self.toggle_music =gui.Toggle(
            self.gui_list,
            *audio_label.rect.move(10,10).bottomleft,
            80,30,"ON",font=12,color=lib.wet_blue,border_radius=10
        )
        self.volume_slider = gui.Slider(
            self.gui_list,
            *self.toggle_music.rect.move(10,0).topright,
            220,30,"Volume",None,border_radius=10,
            color=lib.wet_blue
        )
        self.toggle_music.set_func(
            func=lambda x: [
                self.volume_slider.set_value(x),
                self.toggle_music.set_text("ON" if x else "OFF"),
            ]
        )
        video_control = gui.Panel(
            self.gui_list,
            *audio_control.rect.move(0,10).bottomleft,
            left_panel.rect.w -20,80,border=3,
            border_color=lib.wet_blue,border_radius=10
        )
        video_label = gui.TextBox(
            self.gui_list,
            *video_control.rect.topleft,
            100,30,text = "Video",border_radius=10,color=label_color
        )
        gui.Toggle(
            self.gui_list,
            *video_label.rect.move(10,10).bottomleft,
            160,
            30,
            text="FULLSCREEN",font=12,
            func=lambda x: [
                pygame.display.toggle_fullscreen(),
            ],
            color=lib.wet_blue,
            border_radius=10
        )
        language_control = gui.Panel(
            self.gui_list,
            *video_control.rect.move(0,10).bottomleft,
            left_panel.rect.w -20,80,border=3,
            border_color=lib.wet_blue,border_radius=10
        )
        language_label = gui.TextBox(
            self.gui_list,
            *language_control.rect.topleft,
            140,30,text = "Language",border_radius=10,color=label_color
        )
        for x,lang in enumerate(lib.langs):
            b = gui.Button(
                self.gui_list,
                *language_label.rect.move(10+x*60,10).bottomleft,
                50,30,lang.title(),font=12,color=lib.dark_turquoise if lang == lib.lang else lib.wet_blue,
                uid="lang_button",
                border_radius=10
            )
            b.set_func(
                lambda b=b,lang=lang: 
                [button.set_color(lib.dark_turquoise if button == b else lib.wet_blue) for button in lib.get_by_id(self.gui_list,"lang_button")]+
                [lib.set_lang(lang)]
            
            )
        gui.Button(
            self.gui_list,
            left_panel.rect.x + 10, left_panel.rect.bottom-40,120,30,
            "Back to title",font=12,func=lambda:self.app.set_mode("title"),
            color=lib.wet_blue,border_radius=10
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
        #self.display.blits([[self.app.display_stamp, (0, 0)],[self.dim_surf, (0, 0),None,BLEND_RGB_SUB]])
        self.display.blit(self.dim_surf,(0,0))
        return super().update(dt, mouse, mouse_button, mouse_pressed)
    def on_enter_mode(self):
        self.dim_surf.fill((120,120,120))
        self.dim_surf.blit(self.app.display_stamp,(0,0),None,pygame.BLEND_MULT)