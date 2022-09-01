from pygame.math import Vector2
from lib import *


class Camera:
    def __init__(self, app):
        self.app = app
        self.true_pos = Vector2(0, 0)
        self.int_pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.zoom = 1

    def set_source(self, source):
        self.true_pos = source
        self.int_pos.update(int(self.true_pos.x), int(self.true_pos.y))
        self.target.update(source + Vector2(1, 1))

    def set_target(self, target: Vector2):
        self.target.update(target)
        # print(self.target)

    def set_zoom(self, zoom):
        self.zoom = zoom

    def update(self, dt):
        if self.app.mode in ["game", "edit"]:
            self.true_pos.x += ((self.target.x - self.true_pos.x) - WIDTH / 2) * (
                dt * 10
            )
            self.true_pos.y += ((self.target.y - self.true_pos.y) - HEIGHT / 2) * (
                dt * 10
            )

        self.int_pos.update(int(self.true_pos.x), int(self.true_pos.y))
