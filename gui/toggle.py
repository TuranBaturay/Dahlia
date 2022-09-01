from .button import Button
from .panel import Panel
import pygame
import lib as lib


class Toggle(Button):
    def __init__(
        self, list, x, y, width, height,
        text=None, func=None, color=None, uid="",
        border=0,border_radius=0,border_color=[50,50,50]
    ):
        self.text_panel = None
        self.box = pygame.rect.Rect(0, 0, height // 2.5, height // 2.5)
        self.box.midleft = (10, height // 2)
        self.value = False
        Button.__init__(
            self, list, x, y, width, height, func=func, color=color,text=text,
            uid=uid,border=border,border_color=border_color,border_radius=border_radius
        )
        self.draw()

    def set_text(self, text):
        if not self.text_panel:
            return
        self.text_panel.set_text(text)
        self.draw()

    def get(self):
        return self.value

    def click(self):
        super().click()

    def update(self, dt, mouse_pos, mouse_button, *args):
        Panel.update(self,dt, mouse_pos, mouse_button)
        if self.mouse_in:
            if mouse_button[1] and not self.disabled:
                self.click()
            if mouse_button[3] and not self.disabled:
                self.right_click()
        if self.feedback > 0:
            self.feedback -= 60 * dt
            if self.feedback <= 0:
                if self.func:
                    self.toggle()
                self.feedback = 0
            self.draw()

    def toggle(self, value=None, callback=True):
        self.value = not self.value if value == None else value
        if self.func and callback:
            self.func(self.value)
        self.draw()

    def draw(self):
        super().draw()
        if self.value:
            pygame.draw.circle(self.image, lib.dark_green, self.box.center,self.box.w//2)
        else:
            pygame.draw.circle(self.image, lib.darker_red, self.box.center,self.box.w//2)
        pygame.draw.circle(self.image, lib.cloud_white, self.box.center,self.box.w//2,2)
        # pygame.draw.rect(self.image,(100,0,100), self.rect,3)
