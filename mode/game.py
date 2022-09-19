from .mode import Mode
import gui as gui
import lib as lib
from pygame.math import Vector2
import pygame
from pygame.locals import *


class Game(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.bg = pygame.image.load("Assets/images/bg.png").convert()
        self.bg_scaled = pygame.surface.Surface((2160, 1200))
        pygame.transform.scale(self.bg, (2160, 1200), self.bg_scaled)

    def toggle_update_player(self, toggle):
        self.update_player = toggle

    def spawn(self):
        self.app.player.go_to(self.app.level.spawn_point, anchor="s"),
        self.app.player.set_cat(self.app.cat),
        self.app.cat.go_to(self.app.player.rect.midbottom, anchor="s"),
        self.app.camera.set_source(Vector2(*self.app.player.pos))

    def init_gui(self):
        self.health_meter = gui.Meter(
            self.gui_list,
            50,
            50,
            200,
            25,
            color=lib.dark_red,
            border_radius=10,
            bg_color=[30, 30, 30],
        )
        self.magic_meter = gui.Meter(
            self.gui_list,
            50,
            80,
            150,
            25,
            color=lib.dark_green,
            border_radius=10,
            bg_color=[30, 30, 30],
        )

    def active_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.health_meter.set_value(self.app.player.health_level)
        self.magic_meter.set_value(self.app.player.magic_level)

        self.display.fill((0, 0, 0))
        self.display.blit(
            self.bg_scaled,
            (0, 0),
            (
                self.app.camera.int_pos.x / 10,
                200 + self.app.camera.int_pos.y / 10,
                lib.WIDTH,
                lib.HEIGHT,
            ),
        )

        self.app.level.update(dt)
        res = self.app.level.blit_layers(hitbox=self.app.show_hitbox)
        self.app.debugger.set("CPH", str(res))
        self.app.character_group.update(dt)
        if self.app.playing_character.rect.y > 8000:
            self.app.load_level(self.app.selected_level)
        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
        self.blit_gui()

        target = Vector2(
            self.app.playing_character.rect.centerx,
            self.app.playing_character.rect.y - lib.HEIGHT / 16,
        )
        if self.app.player.state == "hiding":
            target.y += min(self.app.player.hiding_counter, 200)
        self.app.camera.set_target(target)
        self.app.camera.update(dt)

    def onkeydown(self, key, caps=None):
        player = self.app.get_character()
        player.on_key_down(key)

        if key == K_e:
            self.app.set_mode("edit")
        elif key == K_s:
            self.spawn()
        elif key == K_u:
            lib.post_dialogs_by_id("test")
        elif key == K_m:
            player.health_level += 10
        elif key == K_n:
            player.health_level -= 10
        elif key == K_k:
            self.app.screen_shake()
        elif key == K_ESCAPE:
            self.app.set_mode("settings")
        elif key == K_q:
            player.go_to(
                [i * 64 for i in self.app.get_virtual_mouse_pos()], anchor="nw"
            )
        elif key == K_y:
            self.app.set_character(
                self.app.cat
                if self.app.get_character() == self.app.player
                else self.app.player
            )
