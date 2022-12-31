from .textbox import TextBox
from .panel import Panel
import pygame
import lib as lib


class Button(Panel):
    def __init__(
        self,
        list,
        x,
        y,
        width,
        height,
        text=None,
        align="center",
        func=None,
        image=None,
        color=[50, 50, 50],
        text_color=lib.cloud_white,
        uid="",
        border_radius=0,
        font=lib.default_text_size,
        border=0,
        border_color=[50, 50, 50],
        camera=None,
    ):
        self.text_panel = None
        self.disabled = False
        self.func = func
        self.right_click_func = None
        self.feedback = 0
        self.mouse_in_flag = False
        self.color = color

        self.img = image
        super().__init__(
            list,
            x,
            y,
            width,
            height,
            color=color,
            uid=uid,
            border_radius=border_radius,
            border=border,
            border_color=border_color,
            camera=camera,
        )
        self.highlight = self.image.copy()
        pygame.draw.rect(
            self.highlight,
            (10, 10, 10),
            (0, 0, *self.rect.size),
            0,
            self.border_radius,
        )
        self.dim = self.image.copy()
        pygame.draw.rect(
            self.dim,
            (35, 30, 30),
            (0, 0, *self.rect.size),
            0,
            self.border_radius,
        )
        self.text_panel = None
        if text:
            self.text_panel = TextBox(
                None,
                0,
                0,
                width,
                height,
                text="",
                text_color=text_color,
                align=align,
                color=(0, 0, 0, 0),
                border_radius=self.border_radius,
                font=font,
            )

        self.set_text(text)
        self.draw()

    def set_img(self, img):
        self.img = img
        self.image.convert_alpha()
        # self.color = (0, 0, 0, 0)
        self.draw()

    def set_text(self, text):
        if not self.text_panel:
            return
        self.text_panel.set_text(text)
        # print("textbox set text : ",text)
        self.draw()

    def get_text(self):
        if not self.text_panel:
            return None
        return self.text_panel.get_text()

    def set_func(self, func=None):
        self.func = func

    def set_right_click_func(self, func=None):
        if func:
            self.right_click_func = func

    def set_color(self, color):
        super().set_color(color)
        if self.text_panel:
            self.text_panel.set_text(self.text_panel.text, color)
        self.draw()

    def right_click(self):
        if self.right_click_func:
            self.right_click_func()

    def click(self):
        if not self.visible:
            return
        if self.feedback:
            return
        self.feedback = 10
        # print("Click")
        self.draw()

    def mouse_enter(self):
        self.draw()

    def mouse_leave(self):
        self.draw()

    def enable(self):
        self.disabled = False
        self.draw()

    def disable(self):
        self.feedback = 0

        self.disabled = True
        self.draw()

    def update(self, dt, mouse_pos, mouse_button, *args):
        super().update(dt, mouse_pos, mouse_button)
        if self.mouse_in:
            if mouse_button[1] and not self.disabled:
                self.click()
            if mouse_button[3] and not self.disabled:
                self.right_click()
        if self.feedback > 0:
            self.feedback -= 60 * dt
            if self.feedback <= 0:
                if self.func:
                    self.func()
                self.feedback = 0
            self.draw()

    def draw(self):

        if self.text_panel:
            self.text_panel.draw()
        super().draw()

        if self.img:
            self.image.blit(self.img, (0, 0))
        if self.disabled:
            self.image.blit(self.dim, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        if self.feedback > 0 or (self.mouse_in and not self.disabled):

            if self.text_panel:
                self.image.blit(self.text_panel.image, (0, 0))

            if self.feedback > 0:
                # print("---------------------CLICK",self.text_panel.text,self.feedback)

                pygame.draw.rect(
                    self.image,
                    (200, 200, 200),
                    (0, 0, self.rect.w, self.rect.h),
                    int(self.feedback + 3),
                    self.border_radius,
                )
            else:
                self.image.blit(
                    self.highlight, (0, 0), special_flags=pygame.BLEND_RGB_ADD
                )
        else:
            if self.text_panel:
                self.image.blit(self.text_panel.image, (0, 0))
