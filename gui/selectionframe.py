import gui as gui
import lib as lib
class SelectionFrame(gui.Panel):
    def __init__(
        self,
        gui_list=None,
        x=0,
        y=0,
        width=100,
        height=100,
        color=None,
        border=0,
        border_color=lib.dark_gray,
        border_radius=0,
        uid="",
        camera=None
    ) -> None:
        super().__init__(
            gui_list, x, y, width, height,
            color, border, border_color, border_radius,
            uid, camera=camera
        )
        self.fixed = False
        self.set_up = False
        self.source = (0, 0)
        self.hide()

    def update(self, dt, mouse, mouse_button, mouse_pressed=None):
        super().update(dt, mouse, mouse_button, mouse_pressed)
        if self.camera:
            mouse_pos = [mouse[0],mouse[1]]

        if not self.fixed and mouse_button[1]:
            self.source = mouse_pos
            self.show()
            self.set_up = True

        if self.set_up and not mouse_pressed[0]:
            self.set_up = False
            if self.source == mouse_pos:
                self.hide()
            # print("stop",mouse_pressed)
        if self.set_up:
            if mouse_pos[0] < self.source[0]:
                self.origin.x = mouse_pos[0]
                self.rect.w = self.source[0] - mouse_pos[0]
            else:
                self.rect.w = mouse_pos[0] - self.source[0]
                self.origin.x = self.source[0]
            if mouse_pos[1] < self.source[1]:
                self.origin.y = mouse_pos[1]
                self.rect.h = self.source[1] - mouse_pos[1]
            else:
                self.rect.h = mouse_pos[1] - self.source[1]
                self.origin.y = self.source[1]
            
        self.update_pos()

    def draw(self):
        pass
        #super().draw()