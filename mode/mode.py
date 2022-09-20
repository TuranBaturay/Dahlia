from main import App
import pygame


class Mode:
    def __init__(self, app: App, display) -> None:
        self.display = display
        self.app = app
        self.gui_list = []
        self.state = ""
        self.exit_event = None
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

