from layer import Layer
import lib as lib
import pygame.time
from pygame.locals import SRCALPHA
from pygame.math import Vector2


class Level:
    def __init__(self, display, game):
        self.size = 4
        self.chunk_size = 8
        self.display = display
        self.total = 0
        self.game = game
        self.camera = game.camera
        self.layers = []
        self.layer_order = []
        self.layer_count = 0
        self.last_camera_value = Vector2(0, 0)
        self.spawn_point = Vector2(32, 32)

        self.num = [
            (0, 0),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
        ]

        # Pre_rendered border surfaces
        self.chunk_border = pygame.surface.Surface(
            (self.chunk_size * 64, self.chunk_size * 64)
        )
        self.tile_border = pygame.surface.Surface((64, 64))
        self.tile_border.set_colorkey((0, 0, 0))
        self.chunk_border.set_colorkey((0, 0, 0))

        pygame.draw.rect(self.tile_border, (200, 100, 200), (0, 0, 64, 64), 2)
        pygame.draw.rect(
            self.chunk_border, (100, 200, 100), (0, 0, *self.chunk_border.get_size()), 2
        )
        self.add_layer()

    def set_spawn_point(self, x, y):
        self.spawn_point.update(x, y)

    def format(self):
        data = {}
        data["size"] = self.get_size()
        data["chunk_size"] = self.chunk_size
        data["layers"] = []
        data["spawn"] = list(self.spawn_point)
        for layer in self.layers:
            data["layers"].append([layer[0], layer[1].format()])
        return data

    def load(self, data):
        if not data:
            return False
        print("Loading level")
        start = pygame.time.get_ticks()

        self.total = 0
        self.layer_count = 0
        self.chunk_size = data["chunk_size"]
        self.size = data["size"]
        self.spawn_point = (
            Vector2(*data["spawn"]) if "spawn" in data else Vector2(32, 32)
        )
        self.layers = []

        for i, value in enumerate(data["layers"]):
            id = value[0]
            layer_data = value[1]
            self.add_layer(id)
            if layer_data:
                self.layers[i][1].load(layer_data)
                self.total += self.layers[i][1].total

        time = (pygame.time.get_ticks() - start) / 1000
        print(f"level loaded in {time}s")
        return True

    def save_to_file(self, filename="level"):
        path = "levels/" + filename + ".json"
        data = self.format()
        lib.save_data(path, data)

    def level_exists(self, filename):
        path = "levels/" + filename + ".json"
        data = lib.load_data(path)
        return True if data else False

    def get_size(self):
        self.size = max([layer[1].size for layer in self.layers])
        return self.size

    def load_from_file(self, filename):
        path = lib.level_path + filename + ".json"
        data = lib.load_data(path)
        self.load(data)
        return True

    def get_layer_list(self):
        return [value[0] for value in self.layers]

    def get_layer_index(self, layer):
        for i in range(len(self.layers)):
            if self.layers[i][0] == layer:
                return i
        return -1

    def get_layer_name(self, index):
        if index < 0 or index > len(self.layers):
            return None
        return self.layers[index][0]

    def get_layer(self, layer):
        if isinstance(layer, int):
            if layer >= len(self.layers):
                return None
            return self.layers[layer]
        for i in self.layers:
            if i[0] == layer:
                return i[1]
        return None

    def swap_layers(self, index1, index2):
        if (
            index1 < 0
            or index2 < 0
            or index2 >= len(self.layers)
            or index1 >= len(self.layers)
        ):
            return
        self.layers[index1], self.layers[index2] = (
            self.layers[index2],
            self.layers[index1],
        )
        return True

    def set(self, x, y, layer_name, tile_data, update_chunk=True):
        layer = self.get_layer(layer_name)
        if not layer:
            return False
        res = layer.set(x, y, tile_data, update_chunk)
        # if res : self.blit_layers(True)
        return res

    def remove(self, x, y, layer_name):
        layer = self.get_layer(layer_name)
        if not layer:
            return False
        res = layer.remove(x, y)
        # if res : self.blit_layers(True)
        return res

    def get_first(self, x, y):
        for layer in reversed(self.layers):
            if not layer[1].visible:
                continue
            tile = self.get(x, y, layer[0])
            if tile not in [None, 0]:
                return tile
        return None

    def get(self, x, y, layer_name):
        layer = self.get_layer(layer_name)
        if not layer:
            return None
        return layer.get_tile(x, y)

    def add_layer(self, name=None):
        if name == None:
            name = "Layer " + str(self.layer_count + 1)
        self.layers.append(
            [
                name,
                Layer(
                    self.camera,
                    self.size,
                    self.chunk_size,
                ),
            ]
        )
        self.layer_count += 1

    def rename_layer(self, oldlayer, newlayer):
        index = self.get_layer_index(oldlayer)
        if index == -1:
            return False
        self.layers[index][0] = newlayer
        return True

    def get_neighbor_sprites(self, x, y):
        group = []
        for layer in self.layers:
            group.extend(layer[1].get_neighbor_sprites(x, y))
        return group

    def remove_layer(self, layer):
        index = self.get_layer_index(layer)
        if index == -1:
            return False
        self.layers.pop(index)
        return True

    def set_layer_visible(self, layer_name, visible=True):
        layer = self.get_layer(layer_name)
        if not layer:
            return False
        # print("set",layer,"visible : ",visible)
        layer.visible = visible

    def blit_layer(self, layer, hitbox=False):
        # self.surf.fill((0,0,0))
        if layer not in self.get_layer_list():
            return 0
        tmp = self.get_layer(layer)
        counter = 0
        counter += tmp.blit_chunks()
        # self.surf.blit(tmp.surf,(0,0))
        self.display.blit(tmp.surf, (0, 0))
        return counter

    def blit_layers(self, hitbox=False):
        counter = 0
        blit_list = []
        hitbox_blit_list = []

        for layer in self.layers:
            if not layer[1].visible:
                continue

            layer_list, c = layer[1].blit_chunks(self.display, return_list=True)
            blit_list.extend(layer_list)
            counter += c

            if hitbox:
                blit_rect = self.chunk_border.get_rect()
                chunk_list = layer[1].get_visible_chunks()

                for chunk_info in chunk_list:
                    blit_rect.topleft = [
                        chunk_info[i] * self.chunk_size * 64 - self.camera.int_pos[i]
                        for i in [0, 1]
                    ]
                    for tile in chunk_info[2].collision_group:
                        hitbox_blit_list.append(
                            [
                                self.tile_border,
                                tile.rect.move(
                                    -self.camera.int_pos.x, -self.camera.int_pos.y
                                ),
                            ]
                        )
                    if not blit_rect in [i[1] for i in blit_list]:
                        hitbox_blit_list.append([self.chunk_border, blit_rect.copy()])

        self.display.blits(blit_list)
        if hitbox:
            self.display.blits(hitbox_blit_list)
        return counter

    def update(self, dt):
        for layer in self.layers:
            layer[1].update(dt)
