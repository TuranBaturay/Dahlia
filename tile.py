import pygame
from random import randint
import lib as lib


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, data={}):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.rect.Rect(*pos, 64, 64)



        self.interactible = False
        self.animated = False
        self.index = 0
        self.collision = False
        self.flip = False
        self.animation_data = {}
        self.special_attr = {}
        self.set(data)

    def equals(self,tile:"Tile"):
        if not isinstance(tile,Tile):return False
        return all([
            self.index == tile.index,
            self.animated == tile.animated,
            self.collision == tile.collision,
            self.flip == tile.flip,
        ])

    def format(self):
        data = {"index": self.index, "collision": self.collision, "flip": self.flip,"animated":self.animated}
        if self.animated:
            data["animation_data"] = self.animation_data
        if self.special_attr:
            data["special_attr"] = self.special_attr
        return data

    def set(self, data):
        self.special_attr = {}
        self.animation_duration = None
        self.animation_offset = 0
        for key, value in data.items():
            setattr(self, key, value)
        self.interactible = self.index in lib.interactive_tiles
        if self.animated:
            # print(self.animation_duration)
            self.animation_duration = (
                lib.animated_tile_duration[self.index]
                if self.index in lib.animated_tile_duration.keys()
                else [5] * (len(lib.animated_tileset_cache[self.index]) - 1)
            )
            self.animation_indexes = []
            for i, duration in enumerate(self.animation_duration):
                self.animation_indexes.extend([i] * duration)
            self.animation_data = {"duration":self.animation_duration}
            self.set_attribute("animation_offset",randint(0, 100))
            
        else:
            self.animation_duration = []
            self.animation_indexes = []
            self.animation_offset = 0 
            self.animation_data = {}

    def set_attribute(self, key, value):
        self.special_attr[key] = value

    def get_animation_frame(self, counter):
        return self.animation_indexes[
            (counter + self.special_attr["animation_offset"]) % len(self.animation_indexes)
        ]
