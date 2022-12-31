from .mode import Mode
import gui as gui
import lib as lib
import pygame
from pygame.locals import *
import random

class Title(Mode):
    def __init__(self, app, display) -> None:
        self.bg_color = [34, 26, 41]
        super().__init__(app, display)
        self.y_offset = 0
        self.tmp_surf = pygame.Surface((lib.WIDTH,lib.HEIGHT),pygame.SRCALPHA)
    def init_gui(self):
        self.gui_list = []
        x_center = lib.WIDTH // 2
        gui.TextBox(
            self.gui_list,
            x_center - 200,
            lib.HEIGHT // 2 - 250,
            400,
            300,
            "DAHLIA",
            "title",
            [0, 0, 0, 0],
        )
        y_pos = lib.HEIGHT // 2 + 100
        gui.Button(
            self.gui_list,
            x_center - 80,
            y_pos,
            140,
            30,
            "Play",
            font=12,
            color=lib.wet_blue,
            func=self.play,
            border_radius=10,
        )
        y_pos += 40
        gui.Button(
            self.gui_list,
            x_center - 80,
            y_pos,
            140,
            30,
            "Levels",
            font=12,
            color=lib.wet_blue,
            func=lambda: self.app.set_mode("level_viewer"),
            border_radius=10,
        )
        y_pos += 40

        gui.Button(
            self.gui_list,
            x_center - 80,
            y_pos,
            140,
            30,
            "Settings",
            font=12,
            color=lib.wet_blue,
            func=lambda: self.app.set_mode("settings"),
            border_radius=10,
        )
        y_pos += 40

        gui.Button(
            self.gui_list,
            x_center - 80,
            y_pos,
            140,
            30,
            "Quit",
            font=12,
            color=lib.wet_blue,
            func=self.app.quit,
            border_radius=10,
        )

    def play(self):
        print("play")
        self.app.selected_level = "level"
        self.app.load_level(self.app.selected_level)

    def active_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.fill(self.bg_color)
        super().active_update(dt, mouse, mouse_button, mouse_pressed)
    def enter_update(self, dt, mouse, mouse_button, mouse_pressed):

        self.display.fill(self.bg_color)
        self.tmp_surf.fill((0,0,0,0))

        if round(self.y_offset) <=0:
            self.y_offset = 0
            self.state = "active"
        var = 1
        for panel in self.gui_list:
            if not isinstance(panel,gui.Button):
                self.tmp_surf.blit(panel.image,panel.rect.move(0,-self.y_offset*0.7))
                continue
            self.tmp_surf.blit(panel.image,panel.rect.move(-self.y_offset*0.5*var,self.y_offset*var))
            var+=2
        dx = 0-self.y_offset
        self.y_offset += dx * (dt*4)
        self.tmp_surf.set_alpha(255-abs(self.y_offset))
        self.display.blit(self.tmp_surf,(0,0))
    def on_enter_mode(self):
        if self.app.previous_mode != "title":
            self.state ="active"
            return
        self.y_offset = 255
        
        return super().on_enter_mode()
    def onkeydown(self, key, caps=None):
        if self.state == "active":
            if key == K_t:
                self.app.get_input().ask_list(print,[str(random.randint(0,1000)) for _ in range(10)],"TEST")
        