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
        self.min_x = 0

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
        ypos = 20 + self.keys.index(key) * 20
        string = key + ":" + str(value)
        string_render = lib.render_text(string, 26, (200, 200, 200))
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
                counter += 20
                continue
            value = self.data[key]
            string = key + ":" + str(value) if key else str(value)
            string_render = lib.render_text(string, 26, (20, 20, 20))
            blit_list.append(
                [
                    string_render,
                    (
                        self.display_rect.w - string_render.get_rect().w - 20,
                        counter + 2,
                    ),
                ]
            )
            string_render = lib.render_text(string, 26, (200, 200, 200))
            blit_list.append(
                [
                    string_render,
                    (self.display_rect.w - string_render.get_rect().w - 20, counter),
                ]
            )

            counter += 20
            self.display.blits(blit_list)
