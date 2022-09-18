
import sys
from os.path import isfile as os_isfile
from os.path import join as os_join
from os import listdir as os_listdir
from os import chdir as os_chdir

# Set the directory for export aas .exe
if getattr(sys, 'frozen', False):
    os_chdir(sys._MEIPASS)

from level import Level
from player import Player
from cat import Cat
from debugger import Debugger
import mode as mode
from camera import Camera
import lib as lib
import pygame
from pygame.locals import *
from pygame.math import Vector2
from math import cos, floor

pygame.init()
pygame.mixer.init(channels=4)

FLAGS = 0

_screen = pygame.display.set_mode(
    (lib.WIDTH, lib.HEIGHT), FLAGS
)  # main screen - display is blitted on this


# _display = pygame.surface.Surface(
#    (lib.WIDTH, lib.HEIGHT)
# )  # game screen - everything is blitted on here

_display = _screen

_clock = pygame.time.Clock()
icon = pygame.image.load("Assets/icons/icon.png").convert_alpha()
pygame.display.set_caption("Dahlia")
pygame.display.set_icon(icon)
################################################################################################


class App:
    def __init__(self, _display) -> None:
        # Load ressources
        self.debugger = Debugger(_screen)
        self._display = _display
        self.screen = _screen
        self.musics = {}
        music_path = "Audio/music/"
        for file in os_listdir(music_path):
            f = os_join(music_path, file)
            if os_isfile(f) and file[-4:] == ".mp3":
                self.musics[file[:-4]] = pygame.mixer.Sound(f)

        # Rendering

        self.effect_surf = pygame.surface.Surface((lib.WIDTH, lib.HEIGHT))
        self.effect_surf.set_colorkey((255, 255, 255))

        self.ratio = [1, 1]
        self.x_offset = 0
        self.show_hitbox = False
        self.screen_shake = [0, 0, 0, False]

        self.character_sprites = {}

        # Class instances

        self.camera = Camera(self)
        self.player = Player(_display, self)
        self.cat = Cat(_display, self, self.player)
        self.level = Level(_display, self)
        self.bgm_channel = pygame.mixer.Channel(1)

        # Class setup
        self.debugger.toggle_visibility(False)

        # App Logic
        self.load_ressources()

        self.character_group = pygame.sprite.OrderedUpdates(
            self.cat, self.player)
        self.playing_character = None
        self.set_character(self.player)
        self.display_stamp = None

        self.selected_level = "level"

        if lib.get_files_in_dir("levels", ".json") == []:
            self.save_level("level")

        self.level.load_from_file(self.selected_level)
        self.input_mode = mode.Input(self, _display)
        self.mode_dict = {
            "dialog": mode.Dialog(self, _display),
            "game": mode.Game(self, _display),
            "settings": mode.Settings(self, _display),
            "level_viewer": mode.LevelViewer(self, _display),
            "inspector": mode.Inspector(self, _display),
            "edit": mode.Edit(self, _display),
            "title": mode.Title(self, _display),
            "input": self.input_mode,
        }

        print("-" * 30)
        self.vignette_close = 0
        self.vignette_open = lib.WIDTH
        self.vignette_func = None
        self.vignette_source = None
        self.vignette_set_source()

        pygame.mixer.set_reserved(1)
        self.virtual_mouse = [0, 0]
        self.previous_mode = ""
        self.mode = "title"
        self.set_mode("title")

    ################################################################################################

    def get_input(self):
        return self.input_mode

    def get_inspector(self):
        return self.mode_dict["inspector"]

    def set_mode(self, mode, stamp=True,call_exit=True):

        if self.previous_mode and call_exit:
            self.mode_dict[self.mode].on_exit_mode(pygame.event.Event(lib.SET_MODE,args=[mode,stamp,False]))
            
            return
        if stamp:
            self.display_stamp = self.screen.copy()
        self.previous_mode = self.mode
        self.mode = mode
        if mode in self.mode_dict:
            self.mode_dict[mode].on_enter_mode()
        # print("Mode : ",self.mode)
        # print("Previous mode :",self.previous_mode)

    def get_current_tileset(self):
        return self.tileset_list[self.edit_info["tileset_index"]]

    def quit_game(self):
        self.loop = False
        print("Quit")

    def vignette_set_source(self, source=None):
        if source == None:
            source = (lib.WIDTH // 2, lib.HEIGHT // 2)
        self.vignette_source = source

    def vignette_set_func(self, func):
        if self.vignette_close != 0 or self.vignette_open < lib.WIDTH:
            return
        # print("Vignette set HERE")
        self.vignette_func = func
        self.vignette_close = lib.WIDTH

    def load_ressources(self):
        lib.load_animated_tileset()
        lib.load_tileset()
        self.character_sprites = lib.load_character_sprites()

    def load_level(self, filename, mode="game", source=None, skip_vignette=False):
        if not filename:
            return False
        # print("HERE 1")
        if not self.level.level_exists(filename):
            return False
        self.vignette_set_source(source)

        def func(): return [
            self.level.load_from_file(filename),
            self.player.go_to(self.level.spawn_point, anchor="s"),
            self.player.set_cat(self.cat),
            self.cat.go_to(self.player.rect.midbottom, anchor="s"),
            self.camera.set_source(Vector2(*self.player.pos)),
            self.set_mode(mode),
        ]
        if skip_vignette:
            func()
            return True

        self.vignette_set_func(func)
        return True

    def save_level(self, path):
        if not path:
            return False
        self.level.save_to_file(path)
        return True

    def remove_level(self, name):
        if name == "":
            return False
        lib.remove_file(lib.level_path + name + ".json")
        return True

    def music_set_volume(self, value):
        self.bgm_channel.set_volume(value)

    def get_mouse_pos(self):
        pos = Vector2(pygame.mouse.get_pos())
        pos.x -= self.x_offset
        pos.x = pos.x // self.ratio[0]
        pos.y = pos.y // self.ratio[1]
        return pos

    def get_virtual_mouse_pos(self):
        return self.virtual_mouse

    def keyboard_mouse_input(self, keys):

        if not self.debugger.show:
            if keys[K_h] and self.mode in ["game", "edit"]:
                self.show_hitbox = True
            else:
                self.show_hitbox = False
        self.mode_dict[self.mode].onkeypress(keys)

    def onkeydown(self, key, caps=None):
        # Independent key actions
        if key == K_d:
            self.debugger.toggle_visibility()
            self.show_hitbox = self.debugger.visible
        elif key == K_r:
            self.load_ressources()
        self.mode_dict[self.mode].onkeydown(key, caps)

    def shake_screen(self):
        # print("HEY")
        if not self.screen_shake[3]:
            self.screen_shake[3] = True
            self.screen_shake[2] = 0.1

    def screen_shake_update(self):
        c = self.screen_shake[2]
        self.screen_shake[0] = cos(0.05 * c) * cos(1.5 * c) * 40
        self.screen_shake[1] = cos(0.05 * c) * cos(1.5 * c) * 40

        self.screen_shake[2] += 1

        self.camera.true_pos.x += self.screen_shake[0]
        self.camera.true_pos.y += self.screen_shake[1]

    def get_character(self):
        return self.playing_character

    def set_character(self, char):
        if self.playing_character:
            self.playing_character.toggle_control(False)
        self.playing_character = char
        self.playing_character.toggle_control(True)

    def update_vignette(self, _screen, dt):
        if self.vignette_open < lib.WIDTH:

            self.vignette_open = (
                self.vignette_open + 1 + abs(self.vignette_open * (dt * 5))
            )
            if self.vignette_open > 2:
                pygame.draw.circle(
                    self.effect_surf,
                    (255, 255, 255),
                    self.vignette_source,
                    self.vignette_open,
                )

            _screen.blit(self.effect_surf, (0, 0))
        elif self.vignette_close:
            self.effect_surf.fill((0, 0, 0))

            pygame.draw.circle(
                self.effect_surf,
                (255, 255, 255),
                self.vignette_source,
                self.vignette_close,
            )
            self.vignette_close = int(
                self.vignette_close - 1 - self.vignette_close * (dt * 5)
            )
            if self.vignette_close <= 1:
                self.vignette_close = 0
                self.effect_surf.fill((0, 0, 0))
                if self.vignette_func:
                    self.vignette_func()
                    self.vignette_func = None
                self.vignette_open = -200
            _screen.blit(self.effect_surf, (0, 0))

    def get_virtual_pos(self, pos):
        virtual_pos = [
            floor((pos[0] + self.camera.int_pos.x) / 64),
            floor((pos[1] + self.camera.int_pos.y) / 64),
        ]
        return virtual_pos

    def quit(self):
        self.loop = False

    def main(self, _screen, _clock):
        self.loop = True
        mouse_button = {1: False, 2: False, 3: False, 4: False, 5: False}
        caps = False
        last_time = 0
        while self.loop:
            continue_flag = False
            time = pygame.time.get_ticks()
            dt = (time - last_time) / 1000
            last_time = time
            _clock.tick(lib.FPS)
            if self.screen_shake[2] > 30:
                self.screen_shake = [0, 0, 0, False]
            if self.screen_shake[3]:
                self.screen_shake_update()

            mouse_button = {1: False, 2: False, 3: False, 4: False, 5: False}
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.loop = False
                elif (
                    event.type == MOUSEBUTTONDOWN
                    and event.button in mouse_button.keys()
                ):
                    mouse_button[event.button] = True
                elif event.type == lib.SET_MODE:
                    self.set_mode(*event.args)
                elif event.type == lib.DIALOG:
                    if event.action == "RESUME":
                        self.mode_dict["dialog"].resume()
                    elif event.action == "SAY":
                        self.mode_dict["dialog"].queue_append(event.data)
                elif event.type == lib.INPUTBOX:
                    if event.key == "ON":
                        self.set_mode("input")
                    elif self.mode == "input":
                        self.set_mode(self.previous_mode, False)
                        mouse_button = {
                            1: False,
                            2: False,
                            3: False,
                            4: False,
                            5: False,
                        }
                elif event.type == KEYDOWN:
                    if event.mod & pygame.KMOD_SHIFT or event.mod & pygame.KMOD_CAPS:
                        caps = True
                    else:
                        caps = False
                    self.onkeydown(event.key, caps)
                elif event.type == pygame.WINDOWMOVED:
                    continue_flag = True
            if not pygame.key.get_focused() or continue_flag:  # Lower fps when app in Background
                _clock.tick(10)
                self.debugger.set("FPS", str(int(_clock.get_fps())), True)
                self.debugger.update()
                pygame.display.flip()

                continue

            mouse = self.get_mouse_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            self.virtual_mouse = self.get_virtual_pos(mouse)

            self.debugger.set("FPS", str(int(_clock.get_fps())), True)
            self.debugger.set("", str(dt * 1000) + "ms", True)
            self.debugger.set("Resolution", (lib.WIDTH, lib.HEIGHT))
            self.debugger.set("vm", self.virtual_mouse)
            self.debugger.set("m", mouse)
            self.debugger.set("Player position", str(self.player.rect.center))
            self.debugger.set("Player state", self.player.state)

            self.debugger.set("Camera ", self.camera.int_pos)
            self.debugger.set("Camera target", self.camera.target)
            self.debugger.set("Tiles ", f"total : {self.level.total}")
            info = [layer[1].total for layer in self.level.layers]
            self.debugger.set("Layer totals", info)
            self.debugger.set("info", len(self.level.layers))

            self.keyboard_mouse_input(keys)

            if self.mode in self.mode_dict:
                #print(self.mode)
                self.mode_dict[self.mode].update(
                    dt, mouse, mouse_button, mouse_pressed)
            #_screen.blit(_display, (0, 0))
            self.update_vignette(_screen, dt)
            self.debugger.update()
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = App(_display)
    game.main(_screen, _clock)
