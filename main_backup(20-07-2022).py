import pygame
from pygame.locals import *
from pygame import Vector2
from random import randint
from math import cos, floor

pygame.init()
monitor_info = pygame.display.Info()
font = pygame.font.SysFont("Courier Typeface", 22)
big_font = pygame.font.SysFont("Courier Typeface", 42)


def give_aspect_scale(img, bx, by):
    ix, iy = img.get_size()
    if ix > iy:
        # fit to WIDTH
        scale_factor = bx / float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to HEIGHT
        scale_factor = by / float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx / float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return [int(sx), int(sy)]


def remove_color(surf, color):
    surf.set_colorkey(color)
    surf.convert_alpha()
    return surf


def load_image(path, scale):
    surf = pygame.image.load(path).convert()
    surf = pygame.transform.scale(surf, scale)
    surf = remove_color(surf, (255, 0, 255))

    return surf


# def load_tileset(path,scale):
#     spritesheet = pygame.image.load(path).convert()
#     sheet = [spritesheet.subsurface([i*16,0,16,16]) for i in range(spritesheet.get_width()//16)]
#     for i,surf in enumerate(sheet):
#         surf = pygame.transform.scale(surf,scale)
#         sheet[i] =remove_color(surf,(255,0,255))
#     return sheet


def load_tileset(path, scale):
    img = pygame.image.load(path).convert()
    width = img.get_width() // 16
    height = img.get_height() // 16
    sheet = []
    for y in range(height):
        for x in range(width):
            sheet.append(img.subsurface([x * 16, y * 16, 16, 16]))
    for i, surf in enumerate(sheet):
        surf = pygame.transform.scale(surf, scale)
        sheet[i] = remove_color(surf, (255, 0, 255))
    return sheet


WIDTH = 1280  # monitor_info.current_w//2
HEIGHT = 720  # monitor_info.current_h//2
_display = pygame.surface.Surface(
    (WIDTH, HEIGHT), pygame.SRCALPHA
)  # game screen - everything is blitted on here
_screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), RESIZABLE
)  # main screen - display is blitted on this
_clock = pygame.time.Clock()
GRAVITY = 0.8


def render_text(text, font_size=0, color=(255, 255, 255)):

    size = font.size(text) if font_size == 0 else big_font.size(text)
    surf = pygame.surface.Surface(size).convert_alpha()
    string_render = (
        font.render(text, 0, color)
        if font_size == 0
        else big_font.render(text, 0, color)
    )
    surf.blit(string_render, (0, 0))
    surf.set_colorkey((0, 0, 0))
    return surf


class Debugger:
    def __init__(self, _display) -> None:
        self.dict = {}
        self.display = _display
        self.display_rect = self.display.get_rect()
        self.show = True

    def hide(self):
        self.show = False

    def show(self):
        self.show = True

    def toggle_visibility(self):
        self.show = not self.show

    def update(self):
        if not self.show:
            return
        counter = 20
        for key, value in self.dict.items():
            string = key + ":" + str(value)
            string_render = font.render(string, 0, (255, 255, 255))
            self.display.blit(
                string_render,
                (self.display_rect.w - string_render.get_rect().w - 20, counter),
            )
            counter += 20

    def set(self, key, value):
        self.dict[key] = value


class ParticleManager:
    def __init__(self, _display, camera) -> None:
        self.particles = []
        self.max = 500
        self.display = _display
        self.items = 0
        self.cache = {}
        self.gravity = 0.1
        self.friction = 0.8
        self.camera = camera

    def add_particle(self, pos: Vector2):
        vel = Vector2(randint(-5, 5), randint(-5, 0))
        # vel = Vector2(0,0)
        size = 40
        life = 300
        color = [230, 100, 60]
        if len(self.particles) > self.max:
            self.particles[0] = [pos, vel, size, life, color]
        else:
            self.particles.append([pos, vel, size, life, color])
            self.items += 1

    def update(self):
        for particle in self.particles:
            if not particle[2] in self.cache.keys():
                surf = pygame.Surface((particle[2] * 2, particle[2] * 2))
                surf.set_alpha(20)
                surf.fill([30, 10, 0])
                self.cache[particle[2]] = surf

            surf = self.cache[particle[2]]
            pygame.draw.rect(
                self.display,
                particle[4],
                (
                    particle[0].x - particle[2] // 2,
                    particle[0].y - particle[2] // 2,
                    particle[2],
                    particle[2],
                ),
            )
            self.display.blit(
                surf,
                (particle[0].x - particle[2], particle[0].y - particle[2]),
                special_flags=BLEND_RGB_ADD,
            )

            particle[0] += particle[1]
            particle[1].x *= self.friction
            particle[1].y -= self.gravity
            particle[2] -= 1
            particle[3] -= 1
            particle[4] = [min(i + 5, 255) for i in particle[4]]
            if particle[3] <= 0 or particle[2] <= 0:
                self.particles.remove(particle)
                self.items -= 1


class Toggle(pygame.sprite.Sprite):
    def __init__(self, _display, x=0, y=0, text=None):
        self.value = False
        self.display = _display
        self.image = pygame.surface.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.text = None
        if text:
            self.text = render_text(text, 0, (200, 200, 200))
        self.go_to(x, y)

    def get(self):
        return self.value

    def toggle(self, value=None):
        self.value = not self.value if value == None else value

    def go_to(self, x, y):
        self.rect.topleft = (x, y)
        if self.text:
            self.text_rect = self.text.get_rect()
            self.text_rect.left = self.rect.right + 20
            self.text_rect.centery = self.rect.centery

    def update(self, mouse_pos, mouse_button):
        if self.rect.collidepoint(mouse_pos):
            if mouse_button[1]:
                self.toggle()
        self.draw()

    def draw(self):
        if self.value:
            pygame.draw.rect(self.display, (40, 100, 40), self.rect)
        pygame.draw.rect(self.display, (200, 200, 200), self.rect, 3)
        if self.text:
            self.display.blit(self.text, self.text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, _display, game):
        pygame.sprite.Sprite.__init__(self)
        self.vel = Vector2(0, 0)
        self.movement_keys = [K_UP, K_RIGHT, K_LEFT, K_DOWN]
        self.game = game
        self.speed = 2
        self.camera = game.camera
        self.jump_force = 12
        self.state = "idle"
        self.state_lock = False
        self.on_ground = False
        self.face_right = True
        self.animation_dict = {}
        self.load_animations(
            "Assets/Animation/Dahlia/run.png", [5, 5, 5, 5]
        )  # run animation
        self.load_animations(
            "Assets/Animation/Dahlia/idle.png", [20, 20]
        )  # idle animation
        self.load_animations("Assets/Animation/Dahlia/hide.png", [10, 4, 7, 1000])
        self.load_animations("Assets/Animation/Dahlia/fall.png", [10000])
        self.load_animations("Assets/Animation/Dahlia/jump.png", [3, 10000])
        self.display = _display
        self.animation_counter = 0
        self.image = self.animation_dict["idle"][0]
        self.rect = pygame.rect.Rect(0, 0, 32, 52)
        self.player_tile = Vector2(0, 0)
        self.draw_rect = pygame.rect.Rect(0, 0, 64, 64)
        self.hitbox = pygame.rect.Rect(
            0, 0, self.rect.w, self.rect.h
        )  # only for debuuging in self.draw_hitbox

    def go_to(self, new_pos, anchor="center"):
        pos = Vector2(new_pos)
        if anchor == "center":
            pos -= Vector2(self.rect.w // 2, self.rect.h // 2)
        elif anchor == "nw":
            pass
        elif anchor == "n":
            pos -= Vector2(self.rect.w // 2, 0)
        elif anchor == "s":
            pos -= Vector2(self.rect.w // 2, self.rect.h)
        self.rect.topleft = pos
        self.vel = Vector2(0, 0)

    def set_state(self, state, reset=True):
        if self.state_lock:
            return
        self.state = state
        if reset:
            self.animation_counter = 0

    def lock_state(self):
        self.state_lock = True

    def unlock_state(self):
        self.state_lock = False

    def load_animations(self, path, durations):
        filename = path.split("/")[-1].split(".png")[0]
        self.animation_dict[filename] = []
        spritesheet = pygame.image.load(path).convert()
        sheet = [
            spritesheet.subsurface([i * 16, 0, 16, 16]) for i in range(len(durations))
        ]
        for i in range(len(durations)):
            img = img1 = sheet[i]

            img1 = remove_color(img1, (255, 0, 255))
            img1 = pygame.transform.scale(img1, (64, 64))

            for j in range(durations[i]):
                self.animation_dict[filename].append(img1)

    def input(self):
        keys = pygame.key.get_pressed()
        if (
            all(keys[v] == False for v in self.movement_keys)
            and -0.9 < self.vel.y < 0.9
        ):
            self.vel.x = 0
            if self.state != "idle":
                self.set_state("idle")
        if keys[K_DOWN]:
            if self.state != "hide":
                self.set_state("hide")
            self.vel.x = 0
            return
        elif self.state == "hide":
            self.set_state("idle")
        if keys[K_RIGHT]:
            self.vel.x += self.speed
            self.face_right = True
        if keys[K_LEFT]:
            self.vel.x -= self.speed
            self.face_right = False
        if keys[K_UP]:
            if self.on_ground:
                self.set_state("jump")
                self.lock_state()

    def get_tile(self, x, y):
        return self.game.level.get(int(x), int(y))

    def update(self):
        self.vel.x = round(self.vel.x, 2)
        self.vel.y = round(self.vel.y, 2)
        # self.game.debugger.set("Vel",self.vel)
        self.player_tile.x = floor(self.rect.x / 64)
        self.player_tile.y = floor(self.rect.y / 64)

        # handle input
        self.input()
        if self.state == "jump" and self.animation_counter == 1:
            self.unlock_state()
            self.vel.y -= self.jump_force
            self.on_ground = False
        self.vel.y += GRAVITY
        self.vel.y = min(15, self.vel.y)

        # handle state
        if self.on_ground and self.state != "hide":
            if self.vel.x != 0:
                if self.state != "run":
                    self.set_state("run")
            else:
                if self.state != "idle":
                    self.set_state("idle")

        # handle collision
        self.rect.x += self.vel.x
        for tile in self.game.collision_tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                self.vel.x = 0

        self.rect.y += self.vel.y
        for tile in self.game.collision_tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                self.vel.y = 0

        if self.vel.y > 0.9 and self.state != "fall":
            self.set_state("fall")
        # handle animation

        self.vel.x *= 0.6
        self.animation_counter += 1
        if self.animation_counter >= len(self.animation_dict[self.state]):
            self.animation_counter = 0
        self.image = self.animation_dict[self.state][self.animation_counter]
        if not self.face_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.draw()

    def draw(self):
        self.draw_rect.bottom = self.rect.bottom
        self.draw_rect.centerx = self.rect.centerx
        self.draw_rect.x -= self.camera.int_pos.x
        self.draw_rect.y -= self.camera.int_pos.y

        self.display.blit(self.image, self.draw_rect)
        if self.game.show_hitbox:
            self.draw_hitbox()
        # pygame.draw.rect(self.display,(180,120,120),(self.player_tile.x*64,self.player_tile.y*64,64,64),3)
        # pygame.draw.rect(self.display,(250,120,120),self.rect,3,4)
        # pygame.draw.rect(self.display,(200,120,220),self.wall,3)

    def draw_hitbox(self):
        self.hitbox.bottom = self.rect.bottom - self.camera.int_pos.y
        self.hitbox.centerx = self.rect.centerx - self.camera.int_pos.x
        pygame.draw.rect(self.display, (200, 100, 120), self.draw_rect, 3)
        pygame.draw.rect(self.display, (100, 200, 120), self.hitbox, 2)


class Camera:
    def __init__(self, game):
        self.game = game
        self.true_pos = Vector2(0, 0)
        self.int_pos = Vector2(0, 0)
        self.target = Vector2(0, 0)

    def set_target(self, target: Vector2):
        self.target = target

    def update(self):
        if not self.game.edit:
            self.true_pos.x += (self.target.x - self.true_pos.x - WIDTH / 2) / 10
            self.true_pos.y += (self.target.y - self.true_pos.y - HEIGHT / 2) / 10

        self.int_pos = Vector2(int(self.true_pos.x), int(self.true_pos.y))


class Tile(pygame.sprite.Sprite):
    def __init__(self, display, camera, index, image, pos, collision, flip=False):
        pygame.sprite.Sprite.__init__(self)
        self.display = display
        self.camera = camera
        self.collision = collision
        self.set(index, image, pos, collision, flip)

    def format(self):
        return {
            "index": self.index,
            "flip": self.flip,
            "rect": [self.rect.x, self.rect.y, self.rect.w, self.rect.h],
            "collision": self.collision,
        }

    def set(self, index, image, pos, collision, flip=False):
        self.image = image
        self.rect = pygame.rect.Rect(0, 0, 64, 64)
        self.draw_rect = self.rect.copy()
        self.rect.topleft = pos
        self.flip = flip
        self.index = index
        self.collision = collision
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
        self.flip = not self.flip

    def update(self):
        pass

    def draw(self):
        self.draw_rect.x = self.rect.x - self.camera.int_pos.x
        self.draw_rect.y = self.rect.y - self.camera.int_pos.y
        self.display.blit(self.image, self.draw_rect)

    def draw_hitbox(self):
        if self.collision:
            pygame.draw.rect(self.display, (200, 100, 120), self.draw_rect, 3)

    # class Level
    def __init__(self, display, game, collision_group):
        self.width = 32
        self.height = 32
        self.display = _display
        self.total = 0
        self.layer_total = [0, 0, 0]
        self.game = game
        self.camera = game.camera
        self.layers = {}
        self.collision_group = collision_group
        for k in range(3):
            self.layers[k] = [
                [None for j in range(self.width)] for i in range(self.height)
            ]

        for i in range(0, self.width):
            self.set(i, 17, 0, True)

    def is_valid(self, x, y):
        return not (x < 0 or x >= self.width or y < 0 or y >= self.height)

    def get(self, x, y, layer=1):
        if not self.is_valid(x, y):
            return None
        return self.layers[layer][y][x]

    def reload_layer(self, layer):
        for y in range(len(self.layers[layer])):
            for x in range(len(self.layers[layer][y])):
                tile = self.get(x, y, layer)
                if tile == None:
                    continue
                tile = self.layers[layer][y][x]
                tile.set(
                    tile.index,
                    self.game.tileset[tile.index],
                    Vector2(x * 64, y * 64),
                    tile.flip,
                )
                pygame.draw.rect(self.display, (255, 255, 255), tile.rect, 3, 2)

    def reload(self):
        for i in range(3):
            self.reload_layer(i)

    def set(self, x, y, index, collision, flip=False, layer=1):
        # print("Attemp to set ",index,f" at {x},{y} ")
        if (
            index != None
            and (index < 0 or index > len(self.game.tileset))
            or not self.is_valid(x, y)
        ):
            return

        # print("set",collision)
        if self.layers[layer][y][x] != None:
            self.layers[layer][y][x].set(
                index,
                self.game.tileset[index],
                Vector2(x * 64, y * 64),
                collision,
                flip,
            )
            if collision:
                self.collision_group.add(self.layers[layer][y][x])
            else:
                self.collision_group.remove(self.layers[layer][y][x])
            return
        tile = Tile(
            self.display,
            self.camera,
            index,
            self.game.tileset[index],
            Vector2(x * 64, y * 64),
            collision,
            flip,
        )
        self.layers[layer][y][x] = tile
        if collision:
            self.collision_group.add(tile)
        self.total += 1
        self.layer_total[layer] += 1

    def remove(self, x, y, layer=1):
        if not self.is_valid(x, y):
            return
        self.collision_group.remove(self.layers[layer][y][x])
        self.layers[layer][y][x] = None
        self.layer_total[layer] -= 1
        self.total -= 1

    def flip(self, x, y, layer=1):
        if not self.is_valid(x, y):
            return
        if self.layers[layer][y][x] == None:
            return
        self.layers[layer][y][x].flip()


class Game:
    def __init__(self, _display) -> None:
        self.scale = give_aspect_scale(
            _display, _screen.get_width(), _screen.get_height()
        )
        self.scaled_surf = pygame.transform.scale(_display, self.scale)
        self.dimensions = [
            (_screen.get_width() - self.scaled_surf.get_width()) // 2,
            (_screen.get_height() - self.scaled_surf.get_height()) // 2,
        ]
        self.ratio = [1, 1]
        self.x_offset = 0
        self.edit = False
        # 0 1 2
        # 3 layers : 2 before player draw, 1 after (only layer[1] has collisions)
        self.show_hitbox = False
        self.camera = Camera(self)
        self.pm = ParticleManager(_display, self.camera)
        self.debugger = Debugger(_display)
        self.tileset = load_tileset("Assets/Tiles/tileset.png", (64, 64))
        self.player = Player(_display, self)
        self.collision_tiles = pygame.sprite.Group()
        self.level = Level(_display, self, self.collision_tiles)
        self.player.go_to([16 * 64, 16 * 64], anchor="s")
        self.camera.set_target(self.player.rect.center)

        self.edit_info = {
            "index": 0,
            "alpha_surf": pygame.surface.Surface((64, 64)),
            "page": 0,
            "flip": False,
            "collision": False,
            "tile": Tile(self._display, self.camera, 0, self.tileset[0]),
            "layer": 1,
        }

    # works :)
    def get_mouse_pos(self):
        pos = Vector2(pygame.mouse.get_pos())
        pos.x -= self.x_offset
        pos.x = pos.x // self.ratio[0]
        pos.y = pos.y // self.ratio[1]
        return pos

    def process_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        if keys[K_h]:
            self.show_hitbox = True
        else:
            self.show_hitbox = False
        if self.edit:
            self.camera.true_pos += Vector2(
                10 * (keys[K_RIGHT] - keys[K_LEFT]), 10 * (keys[K_DOWN] - keys[K_UP])
            )

        else:
            if mouse[0]:
                self.pm.add_particle(self.get_mouse_pos())
            if keys[K_p]:
                self.pm.add_particle(self.get_mouse_pos())

    def main(self, _display, _screen, _clock):
        # size = [_screen.get_width(),_screen.get_height()]
        loop = True
        change_scale = True
        render_distance = 16

        # menu bar
        menu_bg = (20, 17, 15)
        tile_bg = (60, 58, 55)
        menu_bar = pygame.surface.Surface((WIDTH, 150))
        menu_bar.fill(menu_bg)
        menu_rect = menu_bar.get_rect()
        menu_rect.x = 0
        menu_rect.y = HEIGHT - 150
        layer_text = render_text("LAYER", 0, (200, 200, 200))
        menu_bar.blit(layer_text, (WIDTH - 160, 60))
        toggle_collision = Toggle(_display, 400, HEIGHT - 100, "Collisions")

        mouse_button = {1: False, 2: False, 3: False, 4: False, 5: False}

        def set_number_surf(surf, num):
            surf.fill((0, 0, 0))
            string = big_font.render(str(num), 0, (200, 200, 200))
            rect = surf.get_rect(center=(16, 16))
            surf.blit(string, rect)
            surf.set_colorkey((0, 0, 0))

        page_num = pygame.surface.Surface((32, 32)).convert_alpha()
        layer_num = pygame.surface.Surface((32, 32)).convert_alpha()

        set_number_surf(page_num, self.edit_info["page"])
        set_number_surf(layer_num, self.edit_info["layer"])

        def render_layer(layer):
            y_range = [
                max(0, center[1] - render_distance),
                min(len(self.level.layers[layer]), center[1] + render_distance),
            ]
            for y in range(y_range[0], y_range[1]):
                if any(index is not None for index in self.level.layers[layer][y]):
                    # print(self.level.matrix[y])

                    x_range = [
                        max(0, center[0] - render_distance),
                        min(
                            len(self.level.layers[layer][y]),
                            center[0] + render_distance,
                        ),
                    ]

                    for x in range(x_range[0], x_range[1]):
                        tile = self.level.get(x, y, layer)
                        if tile != None:
                            # display.blit(tile,(x*64,y*64))
                            tile.draw()
                            if self.show_hitbox:
                                tile.draw_hitbox()

        def update_tile_cursor():
            img = self.tileset[self.edit_info["index"]].copy()
            if self.edit_info["flip"]:
                img = pygame.transform.flip(img, True, False)
            self.edit_info["alpha_surf"]
            self.edit_info["alpha_surf"].fill((0, 0, 0))
            self.edit_info["alpha_surf"].blit(img, (0, 0))
            self.edit_info["alpha_surf"].set_colorkey((0, 0, 0))
            self.edit_info["alpha_surf"].set_alpha(128)

        def set_tile_cursor(index):
            self.edit_info["index"] = index
            update_tile_cursor()

        set_tile_cursor(0)

        while loop:

            _display.fill((47, 67, 74))
            # fps_counter(_display,_clock)
            self.debugger.set("FPS", int(_clock.get_fps()))
            self.debugger.set("Resolution", self.scale)
            self.debugger.set("Player tile", self.player.player_tile)
            self.debugger.set("Edit info", self.edit_info)

            self.debugger.set("Player pos", self.player.rect.center)
            self.debugger.set("Camera ", self.camera.int_pos)

            self.debugger.set(
                "Tiles ",
                f"total : {self.level.total} layers : {self.level.layer_total}",
            )
            self.debugger.set("Player State", self.player.state)
            self.debugger.set("Mouse", mouse_button)

            mouse_button = {1: False, 2: False, 3: False, 4: False, 5: False}

            mouse = self.get_mouse_pos()
            virtual_mouse = [
                floor((mouse.x + self.camera.int_pos.x) / 64),
                floor((mouse.y + self.camera.int_pos.y) / 64),
            ]

            for event in pygame.event.get():
                if event.type == QUIT:
                    loop = False
                if event.type == VIDEORESIZE:

                    self.scale = give_aspect_scale(
                        _display, _screen.get_width(), _screen.get_height()
                    )
                    # size = [event.w,event.h]
                    change_scale = True
                if event.type == KEYDOWN:
                    if event.key == K_e:
                        self.edit = not self.edit
                    if event.key == K_s:
                        self.player.go_to([i * 64 for i in virtual_mouse])

                    if event.key == K_d:
                        self.debugger.toggle_visibility()
                    if event.key == K_r:
                        self.tileset = load_tileset(
                            "Assets/Tiles/tileset.png", (64, 64)
                        )
                        update_tile_cursor()
                        self.level.reload()
                    if event.key == K_p:
                        mouse = self.get_mouse_pos()
                        if not menu_rect.collidepoint(*mouse) and self.edit:
                            tile = self.level.get(
                                virtual_mouse[0], virtual_mouse[1], selected_layer
                            )
                            if tile != None:
                                self.edit_info["index"] = tile.index
                                self.edit_info["flip"] = tile.flip
                            update_tile_cursor()
                if (
                    event.type == MOUSEBUTTONDOWN
                    and event.button in mouse_button.keys()
                ):
                    mouse_button[event.button] = True

            # -----------------------------------------Draw Level

            center = [int(self.player.player_tile.x), int(self.player.player_tile.y)]
            for layer in range(2):
                render_layer(layer)

            selected_layer = self.edit_info["layer"]

            hovered_tile = self.level.get(*virtual_mouse, selected_layer)
            self.debugger.set("In-game mouse", virtual_mouse)

            text = None
            if hovered_tile != None:
                text = hovered_tile.format()
            self.debugger.set("Tile", text)

            self.process_input()

            if not self.edit:
                # _display.blit(torch.image,torch.rect)

                self.player.update()
                # self.pm.add_particle(Vector2(torch.rect.centerx,torch.rect.y+40))
                self.pm.update()
                render_layer(2)
            else:  # ------------------------------------EDIT MODE
                self.player.draw()
                render_layer(2)
                _display.blit(menu_bar, menu_rect)
                mouse = self.get_mouse_pos()
                toggle_collision.update(mouse, mouse_button)
                self.edit_info["collision"] = toggle_collision.get()
                # change_layers:
                if mouse_button[5]:
                    if self.edit_info["layer"] > 0:
                        self.edit_info["layer"] -= 1
                        set_number_surf(layer_num, self.edit_info["layer"])
                if mouse_button[4]:
                    if self.edit_info["layer"] < 2:
                        self.edit_info["layer"] += 1
                        set_number_surf(layer_num, self.edit_info["layer"])
                # TILE PICKER
                i = self.edit_info["page"] * 8

                # FLIP TILE
                if mouse_button[2]:
                    self.edit_info["flip"] = not self.edit_info["flip"]
                    set_tile_cursor(self.edit_info["index"])

                while i < min(len(self.tileset), self.edit_info["page"] * 8 + 8):
                    tile = self.tileset[i]
                    color = None
                    y = HEIGHT - 140 if i % 8 < 4 else HEIGHT - 70
                    rect = pygame.Rect((20 + (i % 4) * 80, y, 64, 64))

                    if i == self.edit_info["index"]:
                        rect.y += cos(pygame.time.get_ticks() / 100) * 2  # Animate
                        color = (255, 150, 150)
                    else:
                        if rect.collidepoint(*mouse):
                            color = (200, 180, 200)
                            if mouse_button[1]:
                                set_tile_cursor(i)
                    pygame.draw.rect(_display, tile_bg, rect)
                    _display.blit(tile, rect)
                    if color:
                        pygame.draw.rect(_display, color, rect, 3)

                    i += 1

                _display.blit(page_num, (4 * 80 + 20, HEIGHT - 90))
                pygame.draw.polygon(
                    _display,
                    (200, 200, 200),
                    (
                        (4 * 80 + 20, HEIGHT - 95),
                        (4 * 80 + 26, HEIGHT - 110),
                        (4 * 80 + 32, HEIGHT - 95),
                    ),
                )
                pygame.draw.polygon(
                    _display,
                    (200, 200, 200),
                    (
                        (4 * 80 + 20, HEIGHT - 60),
                        (4 * 80 + 26, HEIGHT - 45),
                        (4 * 80 + 32, HEIGHT - 60),
                    ),
                )

                _display.blit(layer_num, (WIDTH - 100, HEIGHT - 100))

                # --------------------------------------Place tile mode
                if not menu_rect.collidepoint(*mouse):
                    cursor = pygame.Rect(
                        mouse.x + self.camera.int_pos.x,
                        mouse.y + self.camera.int_pos.y,
                        64,
                        64,
                    )

                    if (
                        pygame.mouse.get_pressed()[0]
                        and self.level.get(*virtual_mouse, selected_layer)
                        != self.edit_info["index"]
                    ):
                        tile = self.level.get(*virtual_mouse, selected_layer)

                        if not (tile != None):
                            # print("set",virtual_mouse,virtual_mouse)
                            self.level.set(
                                *virtual_mouse,
                                self.edit_info["index"],
                                self.edit_info["collision"],
                                self.edit_info["flip"],
                                selected_layer,
                            )
                            # print(self.edit_info['collision'])

                    elif (
                        pygame.mouse.get_pressed()[2]
                        and self.level.get(*virtual_mouse, selected_layer) != None
                    ):
                        # print("remove",virtual_mouse,virtual_mouse)

                        self.level.remove(*virtual_mouse, selected_layer)

                    mouse.y -= 32
                    mouse.x -= 32
                    _display.blit(self.edit_info["alpha_surf"], mouse)
                    pygame.draw.rect(_display, (200, 200, 200), (*mouse, 64, 64), 3)

                # ------------------------------------Mouse in menu
                else:
                    if mouse.x > 340 and mouse.x < 352:

                        if mouse.y < HEIGHT - 90 and (self.edit_info["page"] - 1) >= 0:
                            pygame.draw.polygon(
                                _display,
                                (250, 250, 200),
                                (
                                    (4 * 80 + 20, HEIGHT - 95),
                                    (4 * 80 + 26, HEIGHT - 110),
                                    (4 * 80 + 32, HEIGHT - 95),
                                ),
                                3,
                            )

                            if mouse_button[1]:
                                self.edit_info["page"] -= 1
                                set_number_surf(page_num, self.edit_info["page"])

                        if mouse.y > HEIGHT - 70 and (
                            self.edit_info["page"] + 1
                        ) * 8 < len(self.tileset):
                            pygame.draw.polygon(
                                _display,
                                (250, 250, 200),
                                (
                                    (4 * 80 + 20, HEIGHT - 60),
                                    (4 * 80 + 26, HEIGHT - 45),
                                    (4 * 80 + 32, HEIGHT - 60),
                                ),
                                3,
                            )

                            if mouse_button[1]:
                                self.edit_info["page"] += 1
                                set_number_surf(page_num, self.edit_info["page"])

            self.debugger.update()
            self.camera.set_target(
                Vector2(self.player.rect.centerx, self.player.rect.y - 100)
            )
            self.camera.update()

            self.scaled_surf = pygame.transform.scale(_display, self.scale)

            if change_scale:
                self.ratio = [self.scale[0] / WIDTH, self.scale[1] / HEIGHT]
                self.x_offset = (
                    _screen.get_width() - self.scaled_surf.get_width()
                ) // 2
                self.dimensions = [
                    self.x_offset,
                    (_screen.get_height() - self.scale[1]) // 2,
                ]
                change_scale = False

            _screen.blit(self.scaled_surf, self.dimensions)
            _clock.tick(60)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game(_display)
    game.main(_display, _screen, _clock)
