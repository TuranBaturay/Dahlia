import pygame
from chunk import Chunk
import lib as lib


class Layer:
    def __init__(self, camera, size, chunk_size):
        self.total = 0
        self.size = max(size, 4)  # 4 is min size
        self.chunk_size = chunk_size
        self.camera = camera
        self.chunks = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.visible = True
        self.blit_rect = pygame.rect.Rect(0, 0, 0, 0)
        self.chunks_to_draw = {}
        self.scale_factor = 64 * self.chunk_size

    def load(self, data):
        if data == None:
            return
        self.chunks = []
        self.chunks_to_draw = {}
        data_y = len(data)
        self.size = max(data_y, 4)
        self.total = 0
        for y in range(self.size):
            self.chunks.append([])
            for x in range(self.size):
                if y >= data_y or x >= len(data[y]):
                    self.chunks[y].append(None)
                else:
                    if isinstance(data[y][x], Chunk):
                        self.chunks[y].append(data[y][x])
                        continue
                    if data[y][x] != None:
                        self.chunks[y].append(
                            Chunk(
                                self.chunk_size,
                                (x, y),
                            )
                        )
                        self.chunks[y][x].load(data[y][x], (x, y), self.chunk_size)
                        self.chunks_to_draw[(x, y)] = self.chunks[y][x]
                        # print(x,y,self.chunks[y][x].total,self.total)
                        self.total += self.chunks[y][x].total
                        continue
                    self.chunks[y].append(None)

    def format(self):
        # print(self.total)
        if self.total == 0:
            return None
        data = []
        for y, row in enumerate(self.chunks):
            data.append([])
            for x, chunk in enumerate(row):
                if chunk == None or chunk.total == 0:
                    data[y].append(None)
                else:
                    data[y].append(chunk.format())
        return data

    def double_size(self):
        for y in range(self.size):
            self.chunks.append([])
        self.size *= 2
        print(len(self.chunks))
        self.load(self.chunks)

    def get_total(self):
        return self.total

    def tile_out_of_bounds(self, x, y):
        x = x // self.chunk_size
        y = y // self.chunk_size
        return x < 0 or y < 0 or x >= self.size or y >= self.size

    def get_collision_group(self):
        group = []
        for row in self.chunks:
            for chunk in row:
                if not chunk:
                    continue
                group.extend(chunk.collision_group.sprites())
        return group

    def get_chunk_of_tile(self, x, y):
        if self.tile_out_of_bounds(x, y):
            return 0
        x = x // self.chunk_size
        y = y // self.chunk_size
        return self.chunks[y][x]

    def get_chunk(self, x, y):
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return 0
        return self.chunks[y][x]

    def get_tile_relative_pos(self, x, y):
        return [x % self.chunk_size, y % self.chunk_size]

    def get_neighbor_chunks_of_tile(self, x, y):
        x = int(x // self.chunk_size)
        y = int(y // self.chunk_size)
        # print(x,y)
        num = [
            (0, 0),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (-2, 0),
            (-2, 1),
            (-2, -1),
            (2, -1),
            (2, 0),
            (2, 1),
        ]
        group = []
        for i in num:
            chunk = self.get_chunk(x + i[0], y + i[1])
            if not chunk:
                continue
            group.append([x + i[0], y + i[1], chunk])
        return group

    def get_neighbor_sprites(self, x, y):
        num = [
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
        group = []
        for i in num:
            tile = self.get_tile(x + i[0], y + i[1])
            if not tile or not tile.collision:
                continue
            group.append(tile)
        return group

    def get_tile(self, x, y):
        chunk = self.get_chunk_of_tile(x, y)
        if chunk == 0:
            return 0
        if chunk == None:
            return None
        return chunk.get(*self.get_tile_relative_pos(x, y))

    def remove(self, x, y):
        chunk = self.get_chunk_of_tile(x, y)
        if not chunk:
            return
        tile_pos = self.get_tile_relative_pos(x, y)
        res = chunk.remove(*tile_pos)
        if res:
            self.chunks_to_draw[chunk.pos] = chunk
            self.total -= 1
        return res

    def add_chunk(self, x, y):
        if x < 0 or y < 0:
            return None
        new_chunk = Chunk(self.chunk_size, (x, y))
        self.chunks_to_draw[new_chunk.pos] = new_chunk
        self.chunks[y][x] = new_chunk
        return new_chunk

    def set(self, x, y, tile_data, update_chunk=True) -> bool:
        if x < 0 or y < 0:
            return False
        chunk = self.get_chunk_of_tile(x, y)
        if chunk == 0:
            while chunk == 0:
                self.double_size()
                chunk = self.get_chunk_of_tile(x, y)
        if not chunk:
            chunk_pos = [x // self.chunk_size, y // self.chunk_size]
            chunk = self.add_chunk(*chunk_pos)
        else:
            self.chunks_to_draw[chunk.pos] = chunk
        self.total -= chunk.total
        tile_pos = self.get_tile_relative_pos(x, y)
        res = chunk.set(*tile_pos, tile_data, update_chunk)
        self.total += chunk.total
        return res

    def get_visible_chunks(self) -> list[Chunk]:
        x = int((lib.WIDTH // 2 + self.camera.int_pos.x) // (self.chunk_size * 64))
        y = int((lib.HEIGHT // 2 + self.camera.int_pos.y) // (self.chunk_size * 64))
        num = [
            (0, 0),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (-2, 0),
            (-2, 1),
            (-2, -1),
            (2, -1),
            (2, 0),
            (2, 1),
        ]
        group = []
        for i in num:
            chunk = self.get_chunk(x + i[0], y + i[1])
            if not chunk:
                continue

            group.append([x + i[0], y + i[1], chunk])
        return group

    def blit_chunks(self, display_surf, force_update=False, return_list=False):
        counter = 0
        # start_time = time.time()
        chunk_list = self.get_visible_chunks()
        blit_list = []
        for chunk_value in chunk_list:

            self.blit_rect.update(
                chunk_value[0] * self.scale_factor,
                chunk_value[1] * self.scale_factor,
                self.scale_factor,
                self.scale_factor,
            )
            self.blit_rect.topleft -= self.camera.int_pos
            if not self.blit_rect.colliderect(lib.DISPLAY_RECT):
                continue

            if chunk_value[2].pos in self.chunks_to_draw.keys() or force_update:
                chunk_value[2].draw()
                # print("draw chunk",chunk_value[2].pos,chunk_value[2].draw_each_frame)

                if not chunk_value[2].draw_each_frame:
                    self.chunks_to_draw.pop(chunk_value[2].pos)

            blit_list.append([chunk_value[2].surf, self.blit_rect.copy()])

            counter += 1
        if return_list:
            return blit_list, counter
        display_surf.blits(blit_list)
        return counter

    def reload(self):
        # print("Layer updating")
        for row in self.chunks:
            for chunk in row:
                # print("Chunk is ",chunk)
                if chunk == None:
                    continue
                chunk.draw()

    def update(self, dt):
        chunk_list = self.get_visible_chunks()
        for chunk_value in chunk_list:
            chunk_value[2].update(dt)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def toggle_visibility(self):
        self.visible = not self.visible
