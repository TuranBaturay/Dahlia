from tile import Tile
import pygame
from pygame.locals import SRCALPHA
import lib as lib


class Chunk:
    def __init__(self, size, pos):
        self.pos = pos
        self.size = size
        self.total = 0
        self.collision_group = pygame.sprite.Group()
        self.animation_counter = 0
        self.tiles = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.surf = pygame.surface.Surface((self.size * 64, self.size * 64), SRCALPHA)
        self.draw_each_frame = False

    def load(self, data, pos, size):
        self.pos = pos
        self.total = 0
        self.collision_group.empty()
        self.tiles = [[None for _ in range(size)] for _ in range(size)]

        for coord, tile_data in data.items():
            x, y = coord.split(",")
            self.set(int(x), int(y), tile_data)

    def format(self) -> dict:
        if self.total == 0:
            return None
        data = {}
        for y in range(self.size):
            for x in range(self.size):
                tile = self.tiles[y][x]
                if tile != None:
                    data[f"{x},{y}"] = tile.format()
        return data

    def get(self, x, y):
        if self.out_of_bounds(x, y):
            return -1
        return self.tiles[y][x]

    def set(self, x, y, tile_data, blit_tile=True) -> Tile:
        if self.out_of_bounds(x, y):
            return False
        tile = self.get(x, y)
        new_x = (self.pos[0] * self.size + x) * 64
        new_y = (self.pos[1] * self.size + y) * 64
        if tile == None:
            tile = Tile((new_x, new_y), tile_data)
            self.total += 1

            self.tiles[y][x] = tile

        else:
            tile.set(tile_data)

        if (
            "animation_duration" in tile_data.keys()
            or tile_data["index"] in lib.interactive_tiles
        ):
            self.draw_each_frame = True
        func = (
            self.collision_group.add
            if tile_data["collision"]
            else self.collision_group.remove
        )
        func(tile)
        return True

    def remove(self, x, y) -> bool:
        tile = self.get(x, y)
        if tile == None:
            return False
        self.total -= 1
        if self.total == 0:
            self.draw_each_frame = False
        self.collision_group.remove(self.tiles[y][x])
        self.tiles[y][x] = None
        return True

    def out_of_bounds(self, x, y) -> bool:
        return x < 0 or x >= self.size or y < 0 or y >= self.size

    def draw(self):
        # print("draw chunk")
        counter = int(self.animation_counter)
        self.surf.fill((0, 0, 0, 0))
        tiles_surf_rect = []
        for y in range(len(self.tiles)):
            for x, tile in enumerate(self.tiles[y]):
                if not tile:
                    continue
                if tile.animated:
                    img_index = tile.get_animation_frame(counter)
                    img = lib.animated_tileset_get(tile.index, img_index, tile.flip)
                else:
                    img_index = tile.index
                    img = lib.tileset_get(img_index, tile.flip)
                tiles_surf_rect.append([img, (x * 64, y * 64)])
        self.surf.blits(tiles_surf_rect)

    def update(self, dt):
        dt *= 60
        self.animation_counter += 1 * dt
