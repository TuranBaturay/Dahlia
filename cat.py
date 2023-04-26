import pygame
from pygame.math import Vector2
import lib as lib
from pygame.locals import *
from math import floor
from player import Player


class Cat(Player):
    def __init__(self, _display, game, player):
        pygame.sprite.Sprite.__init__(self)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(0, 0)
        self.movement_keys = [K_UP, K_RIGHT, K_LEFT, K_DOWN]
        self.game = game
        self.display = _display
        self.follow = False
        # self.landing_pg=game.particle_manager.give("land")
        self.speed = 150
        self.player = player
        self.camera = game.camera
        self.jump_force = 900
        self.state = "idle"
        self.control = False
        self.target = 0
        self.transition_to_state = None
        self.state_lock = False
        self.on_ground = False
        self.face_right = True
        self.sfx = {
            "jump": pygame.mixer.Sound("Audio/sfx/jump.wav"),
            "run": pygame.mixer.Sound("Audio/sfx/run.wav"),
            "hide": pygame.mixer.Sound("Audio/sfx/hide.wav"),
        }
        self.interact = None
        self.animation_dict = {}
        self.animation_surf = {}

        self.load_animations("Assets/Animation/Cat/idle.png", [10, 10, 10, 10])
        self.load_animations("Assets/Animation/Cat/run.png", [4, 3, 3, 5] * 2)
        self.load_animations("Assets/Animation/Cat/fall.png", [5, 5])
        self.load_animations("Assets/Animation/Cat/jump.png", [2, 4, 8, 100])
        self.load_animations("Assets/Animation/Cat/fall_transition.png", [2, 2])

        self.interaction_feedback = 0
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
        self.hitbox = pygame.rect.Rect(0, 0, self.rect.w, self.rect.h)

    def toggle_control(self, control: bool):
        super().toggle_control(control)
        if control:
            self.toggle_follow(False)

    def toggle_follow(self, follow: bool = None):
        if follow == None:
            follow = not self.follow
        self.follow = follow
        # print("Cat follow : ->",self.follow)

    def input(self, dt):
        keys = pygame.key.get_pressed()

            
        if not self.control or all(keys[v] == False for v in [K_LEFT, K_RIGHT]) and -self.on_ground:
            self.vel.x = 0
            if self.state not in ["idle"]:
                self.set_state("idle")
        else :
            if keys[K_RIGHT]:
                self.vel.x += self.speed
                self.face_right = True
            if keys[K_LEFT]:
                self.vel.x -= self.speed
                self.face_right = False
        if keys[K_UP] and  self.control:
            if self.on_ground and self.state != "jump":
                self.set_state("jump")
                self.lock_state()

    def on_key_down(self, key):
        if not self.control:
            return
        if key == K_m:
            print("-->", self.state)

    def update(self, dt):

        self.vel.x = round(self.vel.x, 1)
        self.vel.y = round(self.vel.y, 2)
        self.player_tile[0] = floor(self.rect.centerx // 64)
        self.player_tile[1] = floor(self.rect.centery // 64)

        if not self.follow:
            self.input(dt)
        else:
            self.target = self.player.rect.centerx
            if self.player.face_right:
                self.target -= 32
            else:
                self.target += 32
            self.vel.x += (self.target - self.rect.centerx) / (dt * 40)
            self.face_right = self.vel.x > 0
            if abs(self.target - self.rect.centerx) < 10:
                self.rect.centerx = self.target
                self.vel.x = 0
                self.set_state("idle", False)
            if (
                self.vel.x
                and self.on_ground
                and self.state != "jump"
                and 200 > (self.rect.y - self.player.rect.y) > 30
            ):
                self.set_state("jump")
                self.lock_state()

        if self.vel.x != 0 and self.on_ground:
            if self.state != "run":
                self.set_state("run")

        if (
            self.state == "jump" and self.animation_counter >= 6 and self.state_lock
        ):  # 3 is jump frame
            self.unlock_state()
            self.vel.y -= self.jump_force
            self.on_ground = False

        self.movement_y(dt)
        self.handle_collision_y(dt)
        self.movement_x(dt)
        self.handle_collision_x()

        if (
            (self.vel.y > lib.GRAVITY)
            and self.state not in ["fall", "fall_transition"]
            and self.state != "fly"
        ):
            # print("--->", self.vel.y)
            self.set_state("fall_transition", True, "fall")
            self.on_ground = False

        self.animation_counter += 60 * dt

        if self.animation_counter >= len(self.animation_dict[self.state]):
            self.animation_counter = 0
            if self.transition_to_state:
                # print(self.transition_to_state)
                self.unlock_state()
                self.set_state(self.transition_to_state, True)
                self.transition_to_state = None
        self.image = self.get_animation_frame()

        self.draw()

    def draw(self):

        self.draw_rect.bottom = self.rect.bottom
        self.draw_rect.centerx = self.rect.centerx
        self.draw_rect.x -= self.camera.int_pos.x
        self.draw_rect.y -= self.camera.int_pos.y
        self.display.blit(self.image, self.draw_rect)

        if self.game.show_hitbox:
            self.draw_hitbox()

    def draw_hitbox(self):
        self.hitbox.bottom = self.rect.bottom - self.camera.int_pos.y
        self.hitbox.centerx = self.rect.centerx - self.camera.int_pos.x
        pygame.draw.rect(self.display, (200, 100, 120), self.draw_rect, 3)
        pygame.draw.rect(self.display, (100, 200, 120), self.hitbox, 2)
