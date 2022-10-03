from .mode import Mode
import gui as gui
import lib as lib
from pygame.locals import *
import pygame


class Input(Mode):

    def __init__(self, app, display) -> None:
        self.font_size = 12

        super().__init__(app, display)
        self.dim_surf = pygame.Surface((lib.WIDTH, lib.HEIGHT))
        self.display_stamp = None
        self.dim_surf.fill((50, 50, 50))
        self.dim_surf.set_alpha(70)
        self.on_event = pygame.event.Event(lib.INPUTBOX, key="ON")
        self.off_event = pygame.event.Event(lib.INPUTBOX, key="OFF")
        self.cursor_rect = pygame.Rect(0, 0, 3, 20)
        self.blink_speed = 20
        self.animation_counter = 0
        self.max_len = 20
        self.multiline = False
        self.func = None
        self.mode = ""

    def init_gui_text_input(self, width=100, height=100, label="label"):
        self.gui_list = []
        panel = gui.Panel(
            self.gui_list,
            0,
            0,
            width,
            height,
            lib.darker_blue,
            border_radius=10,
            border=3,
            border_color=lib.wet_blue,
        )
        panel.rect.center = lib.DISPLAY_RECT.center
        gui.TextBox(
            self.gui_list,
            *panel.rect.topleft,
            width,
            30,
            color=lib.wet_blue,
            text=label,
            font=self.font_size,
            align="left",
            border_radius=10
        )
        self.db = gui.DialogBox(
            self.gui_list,
            panel.rect.x + 10,
            panel.rect.y + 10,
            width - 20,
            height - 90,
            align="left",
            font=self.font_size,
            border_radius=10,
            padding=10,
            color=lib.darker_blue,
            border=3,
            border_color=lib.wet_blue,
        )
        self.db.rect.move_ip(0, 30)
        cancel = gui.Button(
            self.gui_list,
            0,
            0,
            100,
            30,
            "Cancel",
            font=self.font_size,
            func=self.cancel_text_input,
            border_radius=10,
            color=lib.wet_blue,
        )
        ok = gui.Button(
            self.gui_list,
            0,
            0,
            40,
            30,
            "OK",
            font=self.font_size,
            func=self.validate_text_input,
            color=lib.wet_blue,
            border_radius=10,
        )
        ok.rect.bottomright = panel.rect.bottomright
        ok.rect.move_ip(-10, -10)
        cancel.rect.right = ok.rect.x - 10
        cancel.rect.y = ok.rect.y

    def init_gui_yesno(self,label="label"):
        self.gui_list = []
        width = 300
        height = 100
        panel = gui.Panel(
            self.gui_list,
            0,
            0,
            width,
            height,
            lib.darker_blue,
            border_radius=10,
            border=3,
            border_color=lib.wet_blue,
        )
        panel.rect.center = (lib.WIDTH // 2, lib.HEIGHT // 2)
        gui.TextBox(
            self.gui_list,
            *panel.rect.topleft,
            width,
            30,
            color=lib.wet_blue,
            text=label,
            font=self.font_size,
            align="left",
            border_radius=10
        )     
        no = gui.Button(
            self.gui_list,
            0,
            0,
            40,
            30,
            "No",
            font=self.font_size,
            func=self.cancel_yesno,
            border_radius=10,
            color=lib.dark_red,
        )
        yes = gui.Button(
            self.gui_list,
            0,
            0,
            40,
            30,
            "Yes",
            font=self.font_size,
            func=self.validate_yesno,
            color=lib.dark_turquoise,
            border_radius=10,
        )
        no.rect.bottomright = yes.rect.bottomleft = panel.rect.midbottom
        yes.rect.move_ip(10,-10)
        no.rect.move_ip(-10,-10)

    def init_gui_list(self,data_list,label="label",width=600,height=400):
        self.gui_list = []
        panel = gui.Panel(
            self.gui_list,
            0,0,
            width,height,
            lib.dark_blue,3,lib.wet_blue,10,border_radii=[-1,-1,0,0]
        )
        panel.rect.center = lib.DISPLAY_RECT.center
        label = gui.TextBox(
            self.gui_list,
            *panel.rect.topleft,
            width,
            30,
            color=lib.wet_blue,
            text=label,
            font=self.font_size,
            align="left",
            border_radius=10
        )

        cancel = gui.Button(
            self.gui_list,
            0,0,80,30,"Cancel",func=self.cancel_list,
            color=lib.wet_blue,border_radius=10,font=lib.small_font
        )
        cancel.rect.bottomleft = panel.rect.move(10,-10).bottomleft

        x = 0
        y = 0
        for item  in data_list:
            b = gui.Button(
                self.gui_list,
                0,0,120,25,item,font=lib.small_font,func=lambda item=item: self.validate_list(item),
                color = lib.wet_blue,border_radius=10
            )
            if label.rect.move(10+x*130,10+y*35).bottom + 35 > cancel.rect.top:
                y = 0
                x+=1
            b.rect.topleft = label.rect.move(10+x*130,10+y*35).bottomleft 
            y+=1
            
    def ask_list(self,func,data_list,label):
        self.func = func
        self.init_gui_list(data_list,label=label)
        pygame.event.post(self.on_event)
        self.mode = "list"     

    def ask_text_input(
        self, func, width, height, label="Label", max_len=20, multiline=False
    ):
        self.max_len = max_len
        self.multiline = multiline
        self.init_gui_text_input(width, height, label)
        self.func = func
        pygame.event.post(self.on_event)
        self.place_cursor()
        self.mode = "text"

    def ask_yesno(self,func,label="Label"):
        self.init_gui_yesno(label)
        self.func =func
        pygame.event.post(self.on_event)
        self.mode = "yesno"

    def active_update(self, dt, mouse, mouse_button, mouse_pressed):
        # self.display.blit(self.app.display_stamp,(0,0))
        super().active_update(dt, mouse, mouse_button, mouse_pressed)
        if self.mode == "text":
            if self.animation_counter > self.blink_speed:

                pygame.draw.rect(self.display, (200, 200, 200), self.cursor_rect)

            self.animation_counter += 60 * dt
            if self.animation_counter > self.blink_speed * 2:
                self.animation_counter = 0

#text mode
    def validate_text_input(self):
        pygame.event.post(self.off_event)
        if self.func:
            self.func(self.db.get_text())
        self.clear_text()

    def cancel_text_input(self):
        self.clear_text()
        pygame.event.post(self.off_event)
        if self.func:
            self.func(None)

#yesno mode
    def validate_yesno(self):
        pygame.event.post(self.off_event)
        if self.func:
            self.func(True)

    def cancel_yesno(self):
        pygame.event.post(self.off_event)
        if self.func:
            self.func(False)

#list mode
    def validate_list(self,value):
        pygame.event.post(self.off_event)
        if self.func:
            self.func(value)

    def cancel_list(self):
        pygame.event.post(self.off_event)
        if self.func:
            self.func(None)   

    def get_text(self):
        return self.db.text

    def clear_text(self):
        self.db.clear_text()
        self.place_cursor()

    def place_cursor(self):
        self.cursor_rect.midleft = self.db.text_rect.midright
        self.cursor_rect.move_ip(*self.db.rect.topleft)

    def onkeydown(self, key, caps=None):
        if self.mode == "text":
            if key == K_ESCAPE:
                self.cancel_text_input()
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
                    else:
                        self.validate_text_input()
                elif key == K_DELETE:
                    self.db.clear_text()

            elif key_str.isalnum():
                if len(self.db.text) < self.max_len:
                    self.db.set_text(self.db.text + key_str)

            self.place_cursor()
        elif self.mode == "yesno":
            if key== K_ESCAPE:
                self.cancel_yesno()
            if key == K_RETURN:
                self.validate_yesno()

    def on_enter_mode(self):
        pygame.key.set_repeat(300, 20)
        self.display_stamp = self.display.copy()
        super().on_enter_mode()

    def on_exit_mode(self, exit_event):
        pygame.key.set_repeat()
        self.app.display_stamp = self.display_stamp
        super().on_exit_mode(exit_event)
