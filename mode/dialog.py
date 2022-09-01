from .mode import Mode
import gui as gui
import lib as lib
import pygame
from math import cos


class Dialog(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.commands = []
        self.queue = []
        self.dialog_info = {
            "id": 0,
            "name": "Placeholder",
            "mood": "normal",
            "text": "Placeholder",
            "counter": -1,
            "image": None,
            "sprite_x": 0,
            "panel_x": -lib.WIDTH,
            "text_speed": 1,
            "default_speed": 0.5,
            "wait": False,
        }
        self.pause = pygame.event.Event(lib.DIALOG, action="PAUSE")
        self.resume = pygame.event.Event(lib.DIALOG, action="RESUME")

    def dialog_set_track(self, track, permanent=False):
        if permanent:
            self.app.set_track(track)
            return
        self.previous_track = self.current_track
        self.app.set_track(track)

    def dialog_delay(self, time):
        if time is not int:
            time = int(time)

        self.dialog_info["wait"] = True
        # print("SET WAIT")
        pygame.time.set_timer(self.resume, time)

    def dialog_set_speed(self, speed):
        speed = float(speed)
        if not speed or speed > 5:
            return
        self.dialog_info["text_speed"] = speed

    def dialog_set_image(self, name, mood=""):
        if name in lib.character_sprites.keys():
            sprite_dict = lib.character_sprites[name]
            if mood in sprite_dict.keys():
                if sprite_dict[mood] != self.dialog_info["image"]:
                    self.dialog_info["image"] = sprite_dict[mood]
            elif list(sprite_dict.keys())[0] != self.dialog_info["mood"]:
                self.dialog_info["image"] = list(sprite_dict.values())[0]

            if name != self.dialog_info["name"]:
                self.dialog_info["sprite_x"] = -self.dialog_info["image"].get_width()
        else:
            self.dialog_info["image"] = None
        self.dialog_info["name"] = name
        self.dialog_info["mood"] = mood

    def next(self):
        if len(self.queue) == 0:
            self.app.set_mode(self.app.previous_mode)
            self.display_stamp = None
            if self.previous_track != None:
                self.set_track(self.previous_track)
                self.previous_track = None
            self.dialog_info.update(
                {
                    "name": "Placeholder",
                    "counter": -1,
                    "image": None,
                    "sprite_x": 0,
                    "panel_x": -lib.WIDTH,
                    "text_speed": 1,
                    "default_speed": 0.5,
                    "wait": False,
                }
            )
            return
        name = self.queue[0]["name"]
        mood = self.queue[0]["mood"]
        # print(self.dialog_info['sprite_x'])
        self.dialog_set_image(name, mood)
        # print(self.dialog_info['sprite_x'])

        self.dialog_info.update(self.queue.pop(0))
        # print(self.dialog_queue)

        self.dialog_next_button.disable()
        self.dialog_info["counter"] = 0
        self.dialog_info["text_speed"] = self.dialog_info["default_speed"]

        self.dialog_info["wait"] = False

        self.dialog_label.set_text(name.title())

    def init_gui(self):
        self.dialog_box = gui.DialogBox(
            self.gui_list,
            100,
            lib.HEIGHT - 200,
            lib.WIDTH - 200,
            150,
            color=lib.dark_blue + [245],
            align="left",
            padding=30,
            border_radius=10,
        )
        self.dialog_label = gui.TextBox(
            self.gui_list,
            self.dialog_box.rect.x,
            self.dialog_box.rect.top - 30,
            150,
            30,
            text="",
            color=lib.wet_blue,
            border_radius=10,
        )
        self.dialog_next_button = gui.Button(
            self.gui_list,
            self.dialog_box.rect.right - 100,
            self.dialog_box.rect.bottom - 70,
            50,
            50,
            text=">",
            func=self.next,
            color=lib.wet_blue,
            border_radius=10,
        )

    def update(self, dt, mouse, mouse_button, mouse_pressed):

        self.display.blit(self.display_stamp, (0, 0))
        counter = int(self.dialog_info["counter"])
        dialog_command = None
        if not self.dialog_info["wait"]:
            if counter > len(self.dialog_info["text"]) - 1:
                # print("Enable button")
                self.dialog_next_button.enable()

            if (
                self.dialog_next_button.disabled
                and self.dialog_info["text"][counter] == "#"
            ):
                new_counter = self.dialog_info["text"].find("#", counter + 1)
                if new_counter == -1:
                    new_counter = len(self.dialog_info["text"])
                command = self.dialog_info["text"][counter + 1 : new_counter].split(";")
                if command[0] in self.dialog_codes:
                    # print("Recieved command : ",command)
                    dialog_command = getattr(self, command[0])
                self.dialog_info["text"] = (
                    self.dialog_info["text"][:counter]
                    + self.dialog_info["text"][new_counter + 1 :]
                )

            self.dialog_box.set_text(self.dialog_info["text"][:counter])

            if self.dialog_next_button.disabled:
                target = (
                    self.dialog_info["counter"]
                    + self.dialog_info["text_speed"] * 60 * dt
                )
                code_start = self.dialog_info["text"].find("#", counter, int(target))
                if code_start != -1:
                    target = code_start + 1
                target = min(len(self.dialog_info["text"]), target)
                self.dialog_info["counter"] = target

        # DISPLAY CHARACTER SPRITE
        if self.dialog_info["image"]:
            self.display.blit(
                self.dialog_info["image"], (self.dialog_info["sprite_x"], 0)
            )

            if self.dialog_info["sprite_x"] != 0:
                dx = 0 - self.dialog_info["sprite_x"]
                self.dialog_info["sprite_x"] += dx * (8 * min(dt, 0.1))
                if round(self.dialog_info["sprite_x"]) == 0:
                    self.dialog_info["sprite_x"] = 0

        if self.dialog_info["panel_x"] != 0:
            dx = 0 - self.dialog_info["panel_x"]
            self.dialog_info["panel_x"] += dx * (8 * min(0.1, dt))
            if round(self.dialog_info["panel_x"]) == 0:
                self.dialog_info["panel_x"] = 0

        # DISPLAY GUI
        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
            rect = panel.rect.copy()
            if panel.visible:
                if self.dialog_info["panel_x"]:
                    rect.move_ip(self.dialog_info["panel_x"], 0)

                if panel == self.dialog_next_button and not panel.disabled:
                    rect.move_ip(4 * cos(pygame.time.get_ticks() * (1 / 150)), 0)
                    self.display.blit(panel.image, rect)
                    pygame.draw.rect(
                        self.display, (lib.sky_blue), rect, 3, panel.border_radius
                    )
                else:
                    self.display.blit(panel.image, rect)

        if dialog_command:
            dialog_command(*command[1:])
