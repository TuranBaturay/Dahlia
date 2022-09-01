from main import App


class Mode:
    def __init__(self, app: App, display) -> None:
        self.display = display
        self.app = app
        self.gui_list = []
        self.init_gui()

    def init_gui(self):
        pass

    def blit_gui(self):
        self.display.blits(
            [[panel.image, panel.rect] for panel in self.gui_list if panel.visible]
        )

    def update(self, dt, mouse, mouse_button, mouse_pressed):

        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
        self.blit_gui()

    def onkeydown(self, key, caps=None):
        pass

    def onkeypress(self, keys):
        pass
    def on_enter_mode(self):
        pass
    def on_exit_mode(self):
        pass