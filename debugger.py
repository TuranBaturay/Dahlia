import pygame
import lib as lib
from pygame.locals import SRCALPHA


class Debugger:
    def __init__(self, _display) -> None:
        self.data = {}
        self.persistent = {}
        self.keys = []
        self.display = _display
        self.visible = True
        self.display_rect = _display.get_rect()
        self.max_y = 0
        self.font_size = 12
        self.min_x = 0
        self.line_rect = pygame.Rect(0, 0, 0, 0)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def toggle_visibility(self, value=None):
        if value == None:
            value = not self.visible
        self.visible = value
        # print(self.visible)

    def set(self, key, value, persistent=False):
        if not key in self.keys:
            self.keys.append(key)
        if key in self.data.keys() and value == self.data[key]:
            self.persistent[key] = persistent
            # self.draw()
            return

        self.data[key] = value
        self.persistent[key] = persistent
        string = key + ":" + str(value)
        string_render = lib.render_text(string, self.font_size, lib.cloud_white)
        rect = string_render.get_rect()
        self.min_x = min(self.min_x, rect.w - 20)
        self.max_y += 20

    def update(self):
        self.draw()

    def draw(self):
        blit_list = []
        counter = 20
        for key in self.keys:
            if not self.visible and not self.persistent[key]:
                counter += 22
                continue
            value = self.data[key]
            string = key + ":" + str(value) if key else str(value)
            string_render = lib.render_text(string, self.font_size, (200, 200, 200))
            self.line_rect.update(*string_render.get_rect())
            self.line_rect.topleft = (lib.WIDTH - self.line_rect.w - 20, counter)
            pygame.draw.rect(
                self.display,
                lib.darker_blue,
                self.line_rect.inflate(20, 0),
                border_radius=5,
            )
            blit_list.append([string_render, self.line_rect.copy()])

            counter += 22
        self.display.blits(blit_list)
