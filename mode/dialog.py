from .mode import Mode
import gui as gui
import lib as lib
import pygame
from math import cos,ceil
from pygame.locals import *

class Dialog(Mode):
    def __init__(self, app, display) -> None:
        super().__init__(app, display)
        self.commands = ["set_speed","set_image","set_delay"]
        self.queue = []
        self.default_speed = 0.5
        self.text_speed = self.default_speed
        self.image = None
        self.sprite_offset = 0
        self.gui_offset = - lib.WIDTH
        self.text_len = 0
        self.fcounter = 0.0
        self.text = ""
        self.dialog_info = {
            "id": 0,
            "name": "",
            "mood": "",
            "text": "",
        }
        self.punctiation = [',','!','.','?']
        self.wait = False
        self.pause_event = pygame.event.Event(lib.DIALOG, action="PAUSE")
        self.resume_event = pygame.event.Event(lib.DIALOG, action="RESUME")

    def init_gui(self):
        self.dialog_box = gui.DialogBox(
            self.gui_list,
            100,lib.HEIGHT - 220,
            800,150,
            color=lib.dark_blue + [210],
            align="left",
            padding=30,
            font=18,
            border_radius=10,
        )
        self.dialog_box.rect.centerx = lib.WIDTH//2
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
            self.dialog_box.rect.right +10,
            self.dialog_box.rect.centery - 25,
            50,
            50,
            text=">",
            func=self.next,
            color=lib.wet_blue,
            border_radius=10,
        )


    def set_track(self, track, permanent=False):
        pass

    def set_delay(self, time):
        if time is not int:
            time = int(time)
        if time < 1 : return

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
        
        if name : self.dialog_label.set_text(name.title())

    def next(self):
        self.wait = False
        self.text_len = 0
        self.text_speed = self.default_speed
        self.fcounter = 0.0
        self.dialog_box.set_text("")

        if len(self.queue) == 0:
            self.app.set_mode(self.app.previous_mode)
            self.display_stamp = None
            self.dialog_info = {
                "id": 0,
                "name": "",
                "mood": "",
                "text": "",
            }
            self.gui_offset = - lib.WIDTH
            self.sprite_offset = 0
            self.image = None
            self.text = ""



            return
        name = self.queue[0]["name"] if "name" in self.queue[0] else self.dialog_info["name"]
        mood = self.queue[0]["mood"] if "mood" in self.queue[0] else self.dialog_info["mood"]
        # print(self.dialog_info['sprite_x'])
        self.set_image(name, mood)
        # print(self.dialog_info['sprite_x'])

        self.dialog_info.update(self.queue.pop(0))
        # print(self.dialog_queue)

        self.dialog_next_button.disable()
        self.text = self.dialog_info["text"]

        self.text_len = len(self.text)

    def queue_append(self,data):
        self.queue.append(data)
        if self.app.mode != "dialog":
            self.app.set_mode("dialog")


    def update(self, dt, mouse, mouse_button, mouse_pressed):

        self.display.blit(self.app.display_stamp, (0, 0))
        counter = int(self.fcounter)
        dialog_command = None
        if not self.wait:
            if counter >= self.text_len:
                self.dialog_next_button.enable()
            else:
                #check commands
                if self.text[counter]=="#":
                    next_hashtag_index = self.text.find("#",counter+1)
                    if next_hashtag_index == -1 :
                        next_hashtag_index = self.text_len-1
                    dialog_command = self.text[counter+1:next_hashtag_index].split(";")
                    if dialog_command[0] not in self.commands : dialog_command = None
                    self.text = self.text[:counter] + self.text[next_hashtag_index+1:]
                    self.text_len = len(self.text)

                if self.gui_offset == 0:
                    self.dialog_box.set_text(self.text[:counter+1])

                    self.fcounter = min(self.text_len, self.fcounter + self.text_speed*dt*60)

        # DISPLAY CHARACTER SPRITE

        if self.sprite_offset != 0:
            dx = 0 - self.sprite_offset
            self.sprite_offset += dx * (8 * min(dt, 0.1))
            if round(self.sprite_offset) == 0:
                self.sprite_offset = 0


        if self.gui_offset != 0:
            
            #print(self.dialog_info["panel_x"])
            dx = 0 - self.gui_offset
            self.gui_offset += dx * (8 * min(0.1, dt))
            if round(self.gui_offset) == 0:
                self.gui_offset = 0

        # DISPLAY GUI
        if self.image:
            self.display.blit(
                self.image, (self.sprite_offset, 0)
            )

        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
            if panel.visible:
                rect = panel.rect.move(self.gui_offset,0)
                if panel == self.dialog_label and self.dialog_label.get_text()=="":
                    continue

                elif panel != self.dialog_next_button or  panel.disabled:
                    self.display.blit(panel.image, rect)
                else: #NEXT BUTTON
                    

                    rect = rect.move(4 * cos(pygame.time.get_ticks() * (1 / 150)), 0)
                    self.display.blit(panel.image, rect)
                    pygame.draw.rect(
                        self.display, (lib.sky_blue), rect, 3, panel.border_radius
                    )
        if dialog_command:
            getattr(self,dialog_command[0])(*dialog_command[1:])

    def on_enter_mode(self):
        self.next()

    def onkeydown(self, key, caps=None):
        if key == K_x:
            if not self.dialog_next_button.disabled:
                self.next()
            elif '#' not in self.text[int(self.fcounter)+1:] and not self.wait:
                self.fcounter=self.text_len-1
