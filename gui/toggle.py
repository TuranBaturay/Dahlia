from .button import Button
from .panel import Panel
from .textbox import TextBox
import pygame
import lib as lib


class Toggle(Button):
    def __init__(
        self,
        list,
        x,
        y,
        width,
        height,
        text=None,
        text_color = lib.cloud_white,
        align="left",
        font=lib.default_text_size,
        func=None,
        color=None,
        uid="",
        border=0,
        border_radius=0,
        border_color=[50, 50, 50],
        camera=None,
    ):
        self.text_panel :TextBox = None
        self.box = pygame.rect.Rect(0, 0, height // 2.8, height // 2.8)
        self.box.midleft = (10, height // 2)
        self.value = False
        super().__init__(
            list,
            x,y,
            width,height,
            func=func,
            color=color,
            text=text,
            text_color=text_color,
            align=align,
            font=font,
            uid=uid,
            border=border,
            border_color=border_color,
            border_radius=border_radius,
            camera=camera
        )
        #self.set_text(text)

    def set_text(self, text):
        if not self.text_panel:
            return
        self.text_panel.set_text(text)
        if text : 
            if self.text_panel.align == "center":
                self.text_panel.text_rect.centerx = self.text_panel.text_rect.inflate(-5,0).move(self.box.w+10,0).centerx
                #print(text,"center")

            elif self.text_panel.align == "left":
                #print(text,"left")
                self.text_panel.text_rect.left = self.box.w+10 + self.text_panel.padding
            elif self.text_panel.align == "right":
                self.text_panel.text_rect.right = self.text_panel.text_rect.w - self.text_panel.padding
            self.text_panel.text_rect.centery = self.rect.h // 2
        self.draw()




    def get(self):
        return self.value

    def click(self):
        super().click()

    def update(self, dt, mouse_pos, mouse_button, *args):
        Panel.update(self, dt, mouse_pos, mouse_button)
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
        return self.value

    def draw(self):
        super().draw()

        if self.value:
            pygame.draw.circle(
                self.image, lib.dark_green, self.box.center, self.box.w // 2
            )
        else:
            pygame.draw.circle(
                self.image, lib.darker_red, self.box.center, self.box.w // 2
            )
        pygame.draw.circle(
            self.image, lib.cloud_white, self.box.center, self.box.w // 2, 2
        )
        pygame.draw.rect(self.image,(100,0,100), self.rect,3)
