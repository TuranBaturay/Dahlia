from main import App
import pygame
import lib as lib


class Mode:
    def __init__(self, app: App, display) -> None:
        self.display = display
        self.app = app
        self.gui_list = []
        self.state = ""
        self.exit_event = None
        self.GLIDE_SPEED = 20
        self.X_OFFSET = 0
        self.init_gui()
        

    def init_gui(self):
        pass

    def blit_gui(self):
        self.display.blits(
            [[panel.image, panel.rect] for panel in self.gui_list if panel.visible]
        )

    def update(self, dt, mouse, mouse_button, mouse_pressed):
        if self.state == "active":
            self.active_update(dt, mouse, mouse_button, mouse_pressed)
        elif self.state == "exit":
            self.exit_update(dt, mouse, mouse_button, mouse_pressed)
        elif self.state == "enter":
            self.enter_update(dt, mouse, mouse_button, mouse_pressed)

    def active_update(self, dt, mouse, mouse_button, mouse_pressed):
        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
        self.blit_gui()

    def onkeydown(self, key, caps=None):
        pass

    def onkeypress(self, keys):
        pass

    def exit_update(self, dt, mouse, mouse_button, mouse_pressed):
        pygame.event.post(self.exit_event)
        self.state = ""

    def enter_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.state = "active"

    def on_enter_mode(self):
        self.state = "enter"

    def on_exit_mode(self, exit_event):
        self.state = "exit"
        self.exit_event = exit_event
        
    def on_enter_mode_glide_in(self):
        self.state = "enter"
        self.X_OFFSET = -lib.WIDTH+20

    def glide_in_update(self, dt, mouse, mouse_button, mouse_pressed):
        if round(self.X_OFFSET) >=0:
            self.X_OFFSET = 0
            self.state = "active"
        for panel in self.gui_list:
            if panel.visible : self.display.blit(panel.image,panel.rect.move(self.X_OFFSET,0))
        dx = 0-self.X_OFFSET
        self.X_OFFSET += dx * dt * self.GLIDE_SPEED
        #print(dx,self.X_OFFSET)

    def on_exit_mode_glide_out(self,exit_event):
        self.X_OFFSET = -2
        self.state = "exit"
        self.exit_event = exit_event

    def glide_out_update(self, dt, mouse, mouse_button, mouse_pressed):
        if round(self.X_OFFSET) <=-lib.WIDTH:
            self.X_OFFSET = 0
            self.state = ""
            pygame.event.post(self.exit_event)
            return
        for panel in self.gui_list:
            #print(self.X_OFFSET)
            if panel.visible : self.display.blit(panel.image,panel.rect.move(self.X_OFFSET,0))
        
        self.X_OFFSET += self.X_OFFSET * (dt * self.GLIDE_SPEED)
0