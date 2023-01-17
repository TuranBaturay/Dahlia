from .mode import Mode
import gui as gui
import lib as lib
import pygame
from math import cos
from pygame.locals import *


class Dialog(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.commands = [
            "set_speed",
            "set_image",
            "set_delay",
            "set_color",
            "set_default_color",
        ]
        self.queue = []
        self.default_speed = 0.5
        self.text_speed = self.default_speed
        self.master_commands = []
        self.image = None
        self.sprite_offset = 0
        self.gui_offset = -lib.WIDTH
        self.text_len = 0
        self.fcounter = 0.0
        self.text = ""
        self.dialog_info = {
            "id": 0,
            "name": "",
            "mood": "",
            "text": "",
        }
        self.punctiation = [",", "!", ".", "?"]
        self.wait = False
        self.pause_event = pygame.event.Event(lib.DIALOG, action="PAUSE")
        self.resume_event = pygame.event.Event(lib.DIALOG, action="RESUME")
        self.exiting = False
        self.x_offset_target = 0
        self.first_commands_flag =False
        self.exit_event = None

    def init_gui(self):
        self.dialog_box = gui.DialogBox(
            self.gui_list,
            100,
            lib.HEIGHT - 220,
            800,
            150,
            color=lib.dark_blue + [210],
            align="left",
            padding=30,
            font=18,
            border_radius=10,
        )
        self.dialog_box.rect.centerx = lib.WIDTH // 2
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
            self.dialog_box.rect.right + 10,
            self.dialog_box.rect.centery - 25,
            50,
            50,
            text=">",
            func=self.next,
            color=lib.wet_blue,
            border_radius=10,
        )

    def set_color(self, color):
        self.dialog_box.set_text_color(color)

    def set_default_color(self, color):
        self.dialog_box.set_default_text_color(color)

    def set_track(self, track, permanent=False):
        pass

    def set_delay(self, time):
        if time is not int:
            time = int(time)
        if time < 1:
            return

        self.wait = True
        self.dialog_next_button.disable()
        # print("SET WAIT")
        pygame.time.set_timer(self.resume_event, time)

    def resume(self):
        self.wait = False

    def set_speed(self, speed):
        speed = float(speed)
        if not speed or speed > 5:
            speed = 0.5
        self.text_speed = speed

    def set_image(self, name, mood=""):
        if name in lib.character_sprites.keys():
            sprite_dict = lib.character_sprites[name]
            if mood in sprite_dict.keys():
                if sprite_dict[mood] != self.set_image:
                    self.image = sprite_dict[mood]
            elif list(sprite_dict.keys())[0] != self.dialog_info["mood"]:
                self.image = list(sprite_dict.values())[0]

            if name != self.dialog_info["name"]:
                self.sprite_offset = -self.image.get_width()
        else:
            self.image = None
        self.dialog_info["name"] = name
        self.dialog_info["mood"] = mood

        if name:
            self.dialog_label.set_text(name.title())

    def next(self):
        self.wait = False
        self.text_len = 0
        self.text_speed = self.default_speed
        self.fcounter = 0.0
        self.dialog_box.set_text("")
        self.dialog_box.set_default_text_color(lib.cloud_white)
        self.master_commands = []

        if len(self.queue) == 0:
            self.display_stamp = None
            self.dialog_info = {
                "id": 0,
                "name": "",
                "mood": "",
                "text": "",
            }
            self.text = ""
            self.app.set_mode(self.app.previous_mode)
            return
        
        # print(self.dialog_info['sprite_x'])
        self.dialog_info.update(self.queue.pop(0))
        # print(self.dialog_queue)


        self.dialog_next_button.disable()
        self.text = self.dialog_info["text"]


        self.text_len = len(self.text)
        self.master_commands = self.dialog_info["master_commands"]
        for command in self.master_commands:
            
            self.run_command(command[1:-1].split(',')[1:])
    def queue_append(self, data):
        self.queue.append(data)
        if self.app.mode != "dialog":
            self.app.set_mode("dialog")

    def run_command(self,command):
        if not command[0] in self.commands:return
        #print("recieved command : ", command)
        getattr(self, command[0])(*command[1:])

    def active_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp, (0, 0))
        counter = int(self.fcounter)
        dialog_command = None
        if not self.wait:
            if counter >= self.text_len:
                self.dialog_next_button.enable()
            else:
                # check commands
                if self.text[counter] == "(":
                    command_end = self.text.find(")", counter + 1)
                    if command_end == -1:
                        command_end = self.text_len - 1
                        print("Error : Unmatched parenthesis")
                    dialog_command = self.text[counter + 1 : command_end].split(",")
                    if dialog_command[0] not in self.commands:
                        print("Error : Unknown/Unauthorized command : ", dialog_command)
                        dialog_command = None
                    self.text = self.text[:counter] + self.text[command_end + 1 :]
                    self.text_len = len(self.text)
                elif self.text[counter] == "{":
                    self.fcounter = counter = self.text.find(" ", counter + 1)
                    if self.fcounter < 0:
                        self.fcounter = counter = self.text_len
                elif self.text[counter] == "\\":
                    self.fcounter = counter = counter + 1
                
                self.dialog_box.set_text(self.text[: counter + 1])

                self.fcounter = min(
                    self.text_len, self.fcounter + self.text_speed * dt * 60
                )

        # DISPLAY CHARACTER SPRITE

        # DISPLAY GUI
        if self.image:
            self.display.blit(self.image, (0, 0))

        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
            if panel.visible:
                if panel == self.dialog_label and self.dialog_label.get_text() == "":
                    continue

                elif panel != self.dialog_next_button or panel.disabled:
                    self.display.blit(panel.image, panel.rect)
                else:  # NEXT BUTTON

                    rect = panel.rect.move(
                        4 * cos(pygame.time.get_ticks() * (1 / 150)), 0
                    )
                    self.display.blit(panel.image, rect)
                    pygame.draw.rect(
                        self.display, (lib.sky_blue), rect, 3, panel.border_radius
                    )

        if dialog_command:
            self.run_command(dialog_command)

    def enter_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp, (0, 0))
        if self.image:
            self.display.blit(self.image,(self.X_OFFSET,0))
        super().glide_in_update( dt, mouse, mouse_button, mouse_pressed)
    def exit_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp, (0, 0))
        if self.image:
            self.display.blit(self.image, (self.X_OFFSET, 0))
        self.glide_out_update(dt, mouse, mouse_button, mouse_pressed)



    def on_enter_mode(self,skip:bool=False):
        self.image = None
        self.next()
        self.gui_offset = -lib.WIDTH
        if skip:
            super().on_enter_mode()
            return
        super().on_enter_mode_glide_in()

    def on_exit_mode(self, exit_event):
        self.exiting = True
        self.x_offset_target = -lib.WIDTH
        super().on_exit_mode_glide_out(exit_event)

    def onkeydown(self, key, caps=None):
        if self.state != "active": return
        if key == K_x:
            if not self.dialog_next_button.disabled:
                self.next()
            elif "(" not in self.text[int(self.fcounter):] and not self.wait:
                self.fcounter = self.text_len - 1
