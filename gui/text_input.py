#DEPRECATED
#USE 'input' mode instead

import pygame
import gui as gui
from pygame.locals import *
import lib as lib

# Only 1 per game
class Singleton(type):
    _instances = {}
    _initialized = False
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._initialized = True

        return cls._instances[cls]


class TextInput(gui.Panel, metaclass=Singleton):
    def __init__(
        self,
        gui_list,
        width=None,
        height=None,
        max_len=20,
        blink_speed=20,
        padding=15,
        multiline=False,
        color=lib.darker_blue,
    ):
        if not width and not height:
            return
        super().__init__(
            gui_list, 0, 0, 0,0, color=color, border_radius=10
        )
        self.animation_counter = 0
        self.blink_speed = blink_speed
        self.cursor_rect = pygame.Rect(0, 0, 3, 20)
        self.multiline = multiline
        self.max_len = max_len
        self.func = None
        self.padding = padding


        self.asking_input = False
        self.resize(width,height)
        self.on_event = pygame.event.Event(lib.INPUTBOX, key="ON")
        self.off_event = pygame.event.Event(lib.INPUTBOX, key="OFF", text=self.db.text)


    def resize(self,width,height):

        if width == self.rect.w and height == self.rect.h : return
        if width or height : 
            if width : self.rect.w = width
            if height : self.rect.h = height
            self.rect.center = (lib.WIDTH // 2, lib.HEIGHT // 2)
         
        self.buttons = []
        self.panels = []

        self.label = gui.TextBox(
            self.panels,
            0,
            0,
            width,
            30,
            color=lib.wet_blue,
            align="left",
            text="Label",
            border_radius=10,
        )
        self.db = gui.DialogBox(
            self.panels,
            0,
            30,
            width,
            height - 30,
            color=self.color,
            align="left",
            border_radius=10,
            padding=self.padding,
        )
        super().draw()


    def ask_input(self, func=None, label=None, max_len=None,multiline=False,width=None,height=None):
        self.resize(width,height)
        if func:
            self.func = func
        if max_len != None:
            self.max_len = max_len
        if label:

            self.label.set_text(label)
        self.show()
        pygame.event.post(self.on_event)
        self.asking_input = True

    def cancel(self):
        self.hide()
        self.clear_text()
        self.off_event = pygame.event.Event(lib.INPUTBOX, key="OFF", text=None)
        pygame.event.post(self.off_event)
        if self.func:
            self.func(None)
        self.asking_input = False

    def clear_text(self):
        self.db.clear_text()

    def validate(self):
        self.hide()
        self.off_event = pygame.event.Event(lib.INPUTBOX, key="OFF", text=self.db.text)
        pygame.event.post(self.off_event)
        self.asking_input = False
        if self.func:
            self.func(self.db.text)
        self.clear_text()

    def key_down(self, key, caps):
        if key == K_ESCAPE:
            self.cancel()
            return
        key_str = pygame.key.name(key)
        if caps:
            key_str = key_str.upper()
        if not len(key_str) == 1:
            if key == K_BACKSPACE and len(self.db.text) > 0:
                self.db.set_text(self.db.text[:-1])
            elif key == K_SPACE and len(self.db.text) < self.max_len:
                self.db.set_text(self.db.text + " ")
            elif key == K_RETURN:
                if self.multiline and caps:
                    self.db.set_text(self.db.text + "\n")
                    return
                else:
                    self.validate()
            elif key == K_DELETE:
                self.db.clear_text()

        elif key_str.isalnum():
            if len(self.db.text) < self.max_len:
                self.db.set_text(self.db.text + key_str)

    def get_text(self):
        return self.db.text

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed=None):
        super().update(dt, mouse_pos, mouse_button, mouse_pressed)
        for panel in self.panels+self.buttons:
            panel.update(dt, mouse_pos, mouse_button, mouse_pressed)
        
        if self.asking_input:
            if self.animation_counter > self.blink_speed:

                pygame.draw.rect(self.image, (200, 200, 200), self.cursor_rect)

            self.animation_counter += 60 * dt
            if self.animation_counter > self.blink_speed * 2:
                self.animation_counter = 0

    def draw(self):
        super().draw()

        for panel in self.panels:
            if panel.visible:
                self.image.blit(panel.image, panel.rect)
        for button in self.buttons:
            if button.visible:
                button.draw()
        self.cursor_rect.midleft = self.db.text_rect.midright
        if self.asking_input:
            if self.animation_counter > self.blink_speed:
                pygame.draw.rect(
                    self.image,
                    (200, 200, 200),
                    self.cursor_rect.move(*self.db.rect.topleft),
                )
