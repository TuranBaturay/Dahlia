from math import cos, sin, floor
from random import randint, random
import pygame
import lib as lib
from pygame.math import Vector2

# import ParticleGenerators


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            # print("New")
        return cls._instances[cls]


class ParticleManager(metaclass=Singleton):
    def __init__(self, game, _display, camera) -> None:
        self.camera = camera
        self.display = _display
        self.display_rect = _display.get_rect()
        self.game = game
        self.generators = []
        # self.models = {
        #     "land":ParticleGenerators
        # }
        self.halo_surf_cache = {}

    def update(self, dt):
        for generator in self.generators:
            generator.update(dt)
        self.draw()

    def give(self, model):
        return None
        if not model in self.models.keys():
            return None
        pg = ParticleGenerator(*self.models[model])
        return pg

    def draw(self):
        return
        for generator in self.generators:

            for particle in generator.get_draw_list():
                particle_rect = particle[1].copy()
                if generator.camera_bound:
                    particle_rect.topleft -= self.camera.int_pos
                if not particle_rect.colliderect(self.display_rect):
                    # print("out of bounds")
                    continue
                if particle[0] == "rect":
                    # print("Here")
                    pygame.draw.rect(self.display, particle[2], particle_rect)
                elif particle[0] == "circle":
                    # print("Here")
                    continue
                    pygame.draw.circle(
                        self.display,
                        particle[2],
                        particle_rect.center,
                        particle_rect.w // 2,
                    )
                elif particle[0] == "halo":
                    if not particle_rect.w in self.halo_surf_cache:
                        self.halo_surf_cache[particle_rect.w] = pygame.surface.Surface(
                            (particle_rect.w, particle_rect.w), pygame.SRCALPHA
                        )
                        # self.halo_surf_cache[particle_rect.w].fill((255,0,0))
                    halo_surf = self.halo_surf_cache[particle_rect.w]

                    pygame.draw.circle(
                        halo_surf,
                        particle[2],
                        halo_surf.get_rect().center,
                        particle_rect.w // 2,
                    )
                    self.display.blit(
                        halo_surf,
                        particle_rect.topleft,
                        special_flags=pygame.BLEND_RGB_ADD,
                    )

    def particle_collision_y(self, particle):
        xpos = floor(particle[0].x // 64)
        ypos = floor(particle[0].y // 64)

        group = self.game.level.get_neighbor_sprites(xpos, ypos)
        tile_index = particle[0].collidelist(group)
        if tile_index == -1:
            return particle
        tile = group[tile_index]

        if particle[1].y > 0:
            particle[0].bottom = tile.rect.top
        elif particle[1].y < 0:
            particle[0].top = tile.rect.bottom
        particle[1].y = -particle[1].y * 0.8

        return particle

    def particle_collision_x(self, particle):
        xpos = floor(particle[0].x // 64)
        ypos = floor(particle[0].y // 64)

        group = self.game.level.get_neighbor_sprites(xpos, ypos)
        tile_index = particle[0].collidelist(group)
        if tile_index == -1:
            return particle
        tile = group[tile_index]
        if particle[1].x > 0:
            particle[0].right = tile.rect.left
        elif particle[1].x < 0:
            particle[0].left = tile.rect.right
        particle[1].x = -particle[1].x * 0.8

        return particle
