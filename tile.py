import pygame
from random import randint
import lib as lib


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, data={"index": 0, "collision": False, "flip": False}):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.rect.Rect(*pos, 64, 64)
        self.animated = False
        self.animation_duration = None
        self.animation_indexes = []
        self.interactible = False
        self.animation_offset = 0
        self.special_attr = {}
        self.set(data)

    def format(self):
        data = {"index": self.index, "collision": self.collision, "flip": self.flip}
        if self.animated:
            data["animation_duration"] = self.animation_duration
        if self.special_attr:
            data["special_attr"] = self.special_attr
        return data

    def set(self, data):
        self.special_attr = {}

        self.animated = False
        self.animation_duration = None
        self.animation_offset = 0
        for key, value in data.items():
            setattr(self, key, value)
        self.interactible = self.index in lib.interactive_tiles
        if "animation_duration" in data.keys():
            self.animated = True
            self.animation_indexes = []
            self.animation_offset = randint(0, 100)
            print(self.animation_duration)
            self.animation_duration = (
                lib.animated_tile_duration[self.index]
                if self.index in lib.animated_tile_duration.keys()
                else self.animation_duration
            )
            for i, duration in enumerate(self.animation_duration):
                self.animation_indexes.extend([i] * duration)
        # print(self.format())

    def update(self):
        if not self.animation_duration:
            return

    def add_attribute(self, key, value):
        self.special_attr[key] = value
        self.__setattr__(key, value)

    def get_animation_frame(self, counter):
        return self.animation_indexes[
            (counter + self.animation_offset) % len(self.animation_indexes)
        ]
