import pygame
from pygame import Vector2
from pygame.locals import *
from tile import Tile
from math import floor, cos
import lib as lib


class Player(pygame.sprite.Sprite):
    def __init__(self, _display, game):
        pygame.sprite.Sprite.__init__(self)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(0, 0)
        self.movement_keys = [K_UP, K_RIGHT, K_LEFT, K_DOWN]
        self.game = game
        self.speed = 150
        self.camera = game.camera
        self.jump_force = 700
        self.magic_max = 100
        self.magic_level = 100
        self.health_max = 100
        self.health_level = 100
        self.hiding_counter = 0
        self.animation_dict = {}
        self.animation_surf = {}
        self.state = "idle"
        self.transition_to_state = None
        self.state_lock = False
        self.on_ground = False
        self.face_right = True
        self.interact = None
        self.control = False
        self.cat = None
        self.fly_meter_rate = 1
        self.fly_meter_counter = 1
        self.run_frame = 0

        self.interaction_feedback = 0
        self.interaction_alpha_target = 255

        # Interaction surface 'X' button
        self.interaction_surf = pygame.surface.Surface((64, 64))
        self.interaction_surf.set_colorkey((0, 0, 0))
        pygame.draw.circle(
            self.interaction_surf,
            lib.dark_blue,
            self.interaction_surf.get_rect().center,
            16,
            0,
        )
        pygame.draw.circle(
            self.interaction_surf,
            lib.sky_blue,
            self.interaction_surf.get_rect().center,
            16,
            3,
        )

        pygame.draw.line(self.interaction_surf, lib.cloud_white, (28, 28), (36, 36), 3)
        pygame.draw.line(self.interaction_surf, lib.cloud_white, (36, 28), (28, 36), 3)

        self.interaction_surf.set_alpha(self.interaction_alpha_target)

        self.sfx = {
            "jump": pygame.mixer.Sound("Audio/sfx/jump.wav"),
            "run": pygame.mixer.Sound("Audio/sfx/run.wav"),
            "hide": pygame.mixer.Sound("Audio/sfx/hide.wav"),
        }
        self.load_animations(
            "Assets/Animation/Dahlia/run.png", [5, 5, 5, 5]
        )  # run animation
        self.load_animations(
            "Assets/Animation/Dahlia/idle.png", [10, 10, 10, 10]
        )  # idle animation
        self.load_animations("Assets/Animation/Dahlia/hide.png", [3, 3, 10, 4, 5, 3, 3])
        self.load_animations("Assets/Animation/Dahlia/hiding.png", [100])
        self.load_animations("Assets/Animation/Dahlia/mount_broom.png", [6, 8, 5, 4])
        self.load_animations("Assets/Animation/Dahlia/unmount_broom.png", [3, 8, 5, 4])

        self.load_animations("Assets/Animation/Dahlia/fall.png", [5, 5])

        self.load_animations("Assets/Animation/Dahlia/jump.png", [3, 10000])

        self.load_animations("Assets/Animation/Dahlia/fly.png", [10]*8)

        self.display = _display
        self.animation_counter = 0
        self.image = self.animation_dict["idle"][0]
        self.rect = pygame.rect.Rect(0, 0, 32, 52)
        self.spell_source = Vector2(
            (self.rect.right + 40 * self.face_right)
            + (self.rect.left - 40 * self.face_right * -1),
            self.rect.centery,
        )

        self.player_tile = [0, 0]
        self.draw_rect = pygame.rect.Rect(0, 0, 64, 64)
        self.hitbox = pygame.rect.Rect(
            0, 0, self.rect.w, self.rect.h
        )  # only for debuuging in self.draw_hitbox

    def get_animation_frame(self):
        index = self.animation_dict[self.state][int(self.animation_counter)]
        return self.animation_surf[self.state][index][0 if self.face_right else 1]

    def set_cat(self, cat):
        self.cat = cat

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
        self.pos.update(new_pos)
        self.vel = Vector2(0, 0)

    def set_state(self, state, reset=True, transition_to_state=None):
        if self.state_lock:
            return
        # print("set to ",self.state,state,transition_to_state)
        self.state = state
        if reset:
            self.animation_counter = 0
        self.transition_to_state = transition_to_state
        if transition_to_state:
            self.lock_state()
        if state != "hiding":
            self.hiding_counter = 0

    def toggle_control(self, control: bool):
        self.control = control

    def lock_state(self):
        self.state_lock = True

    def unlock_state(self):
        self.state_lock = False

    def load_animations(self, path, durations):
        filename = path.split("/")[-1].split(".png")[0]
        self.animation_dict[filename] = []
        self.animation_surf[filename] = []

        spritesheet = pygame.image.load(path).convert_alpha()
        sheet = [
            spritesheet.subsurface([i * 16, 0, 16, 16]) for i in range(len(durations))
        ]
        for i in range(len(durations)):
            img = sheet[i]
            img1 = pygame.transform.scale(img, (64, 64))
            img1_flip = pygame.transform.flip(img1, True, False)
            self.animation_surf[filename].append([img1, img1_flip])

            for j in range(durations[i]):
                self.animation_dict[filename].append(i)

    def on_key_down(self, key):
        if not self.control:
            return

            # print(self.rotate)
        elif key == K_DOWN:
            if self.on_ground and not self.state_lock:
                if self.state != "hide":
                    self.set_state("hide", True, "hiding")
                    self.sfx["hide"].play()
        if key == K_x and self.interact and not self.interaction_feedback:
            if self.interact == self.cat:
                self.cat.toggle_follow()
            elif isinstance(self.interact, Tile):
                if self.interact.index == 23:
                    self.interact.index = 22
                elif self.interact.index == 22:
                    self.interact.index = 23
                elif self.interact.index == 14:
                    self.magic_level = min(self.magic_max, self.magic_level + 10)
            self.interaction_feedback = 16

    def input(self, dt):
        keys = pygame.key.get_pressed()

        if not self.control or all(keys[v] == False for v in [K_LEFT, K_RIGHT]) and self.on_ground:
            self.vel.x = 0
            if self.state not in ["idle", "hiding", "fly", "mount_broom"]:
                self.set_state("idle")
        elif self.state in ["fly"]:
            if all(keys[v] == False for v in self.movement_keys):
                self.vel.update(0, 0)

        if keys[K_SPACE] and not self.state_lock and not self.state == "hiding":
            if keys[K_SPACE] and self.magic_level > 0:
                if self.state not in ["fly", "mount_broom"]:
                    self.cat.toggle_follow(False)
                    if self.on_ground:
                        self.vel.y = -self.jump_force
                        self.on_ground = False
                    self.set_state("mount_broom", True, "fly")
        if self.control:
            if keys[K_RIGHT]:
                self.vel.x += self.speed
                self.face_right = True
            if keys[K_LEFT]:
                self.vel.x -= self.speed
                self.face_right = False
            if keys[K_UP]:
                if self.state == "fly":
                    self.vel.y -= self.speed
                elif self.on_ground:
                    self.set_state("jump")
                    self.lock_state()
            if keys[K_DOWN]:

                if self.state == "fly":
                    self.vel.y += self.speed
            elif self.state == "hiding":
                self.set_state("idle")
            if self.state in ["hiding", "hide"]:
                self.vel.update(0, 0)

    def movement_x(self, dt):
        self.vel.x *= lib.FRICTION
        self.pos.x += self.vel.x * dt
        self.rect.x = self.pos.x

    def movement_y(self, dt):
        if self.state not in ["fly", "mount_broom"]:
            self.vel.y += lib.GRAVITY * dt
            self.vel.y = min(lib.GRAVITY // 2, self.vel.y)
        else:
            self.vel.y *= lib.FRICTION
        # print(self.vel.y*dt)
        self.pos.y += self.vel.y * dt

        self.rect.y = self.pos.y

    def handle_collision_x(self):

        for tile in self.game.level.get_neighbor_sprites(*self.player_tile):
            ####print(self.rect)
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                self.vel.x = 0
                self.pos.x = self.rect.x
                break

    def handle_collision_y(self, dt):

        for tile in self.game.level.get_neighbor_sprites(*self.player_tile):
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    if not self.on_ground:
                        self.on_ground = True
                        if self.state == "fly":
                            self.set_state("unmount_broom", True, "idle")
                        if self.vel.y > 12:
                            # self.landing_pg.go_to(self.rect.centerx,self.rect.bottom+10)
                            # self.landing_pg.add_particle(20)
                            self.sfx["run"].play()
                            self.run_frame = 1
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                self.vel.y = 0
                self.pos.y = self.rect.y
                return
        # print("--->", self.vel.y*dt,"gravity :",lib.GRAVITY*dt)
        if (self.vel.y * dt > 1) and self.state not in ["fly", "fall"]:
            self.set_state("fall")
            self.on_ground = False

    def update(self, dt):

        self.player_tile[0] = floor(self.rect.centerx // 64)
        self.player_tile[1] = floor(self.rect.centery // 64)

        if self.state in ["fly", "mount_broom"]:
            self.fly_meter_counter -= 10 * dt
            if self.fly_meter_counter <= 0:
                self.magic_level -= 1
                if self.magic_level < 0:
                    self.magic_level = 0
                    self.set_state("fall")

                self.fly_meter_counter = self.fly_meter_rate
            if self.on_ground and self.state == "fly":
                self.set_state("unmount_broom", True, "idle")

        # handle input
        self.input(dt)
        # handle state

        # print("yvel : ",self.vel.y)

        if self.on_ground and self.state not in ["hiding"]:
            if self.vel.x != 0:
                if self.state != "run":
                    self.set_state("run")
                    self.run_frame = 0

                elif round(self.animation_counter) == 5 and not self.run_frame:
                    self.sfx["run"].play()
                    self.run_frame = 1
        else:
            self.hiding_counter += 100 * dt
        # print(self.animation_counter)
        if (
            self.state == "jump" and self.animation_counter >= 4 and self.state_lock
        ):  # 3 is jump frame
            self.unlock_state()
            self.vel.y -= self.jump_force
            self.sfx["jump"].play()
            # print(self.animation_counter,"Jump",self.vel.y)
            self.on_ground = False

        # handle collision
        self.movement_y(dt)
        self.handle_collision_y(dt)
        self.movement_x(dt)
        self.handle_collision_x()
        # if self.state == "fall":print(dt)

        # handle animation
        if self.interaction_feedback > 1:
            self.interaction_feedback -= 60 * dt
            if self.interaction_feedback <= 1:
                self.interaction_feedback = 0
        if not self.interaction_feedback:

            self.interact = None
            if self.control:
                if (
                    self.draw_rect.colliderect(self.cat.draw_rect)
                    and self.control
                    and self.on_ground
                ):
                    self.interact = self.cat
                else:
                    tile_list = [
                        layer[1].get_tile(self.player_tile[0], self.player_tile[1])
                        for layer in self.game.level.layers
                    ]
                    for tile in tile_list:
                        if tile and tile.interactible:
                            self.interact = tile
                if self.interact:
                    delta = abs(self.rect.centerx - self.interact.rect.centerx)
                    if delta <= 16:
                        self.interaction_alpha_target = 255
                    else:
                        self.interaction_alpha_target = 120

                else:
                    self.interaction_alpha_target = 0

        self.animation_counter += 60 * dt
        self.interaction_surf.set_alpha(
            self.interaction_feedback
            + self.interaction_surf.get_alpha()
            + 0.2 * (self.interaction_alpha_target - self.interaction_surf.get_alpha())
        )
        if self.animation_counter >= len(self.animation_dict[self.state]):
            self.animation_counter = 0
            self.run_frame = 0
            if self.transition_to_state:
                self.unlock_state()
                self.set_state(self.transition_to_state, True)
                self.transition_to_state = None
        self.draw()

    def draw(self):
        self.image = self.get_animation_frame()

        self.draw_rect.bottom = self.rect.bottom
        self.draw_rect.centerx = self.rect.centerx
        self.draw_rect.x -= self.camera.int_pos.x
        self.draw_rect.y -= self.camera.int_pos.y

        if self.state == "fly":
            self.draw_rect.y += 5 * cos(pygame.time.get_ticks() / 100)
        self.display.blit(self.image, self.draw_rect)

        if self.interact or self.interaction_feedback:

            interact_rect = self.interact.rect.move(
                -self.camera.int_pos.x, -self.camera.int_pos.y
            )
            interact_rect.move_ip(
                0, -self.hitbox.h - 3 * cos(pygame.time.get_ticks() / 200)
            )
            if self.interaction_feedback > 0:
                surf_copy = self.interaction_surf.copy()
                pygame.draw.circle(
                    surf_copy,
                    lib.cloud_white,
                    self.interaction_surf.get_rect().center,
                    int(32 - self.interaction_feedback),
                    int(self.interaction_feedback),
                )

                self.display.blit(surf_copy, interact_rect)

            else:
                self.display.blit(self.interaction_surf, interact_rect)

        if self.game.show_hitbox:
            self.draw_hitbox()

    def draw_hitbox(self):
        self.hitbox.bottom = self.rect.bottom - self.camera.int_pos.y
        self.hitbox.centerx = self.rect.centerx - self.camera.int_pos.x
        pygame.draw.rect(self.display, (200, 100, 120), self.draw_rect, 3)
        pygame.draw.rect(self.display, (100, 200, 120), self.hitbox, 2)
