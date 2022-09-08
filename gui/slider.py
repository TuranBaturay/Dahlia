from .textbox import TextBox
from .panel import Panel
import pygame
import lib as lib


class Slider(Panel):
    def __init__(
        self,
        list,
        x,
        y,
        width,
        height,
        text=None,
        font=lib.default_text_size,
        func=None,
        range=None,
        color=lib.wet_blue,
        uid="",
        camera=None,
        border_radius = 0,
        border= 0,
        border_color = [50,50,50]
    ):
        self.disabled = False
        self.func = func
        self.mouse_in_flag = False
        self.mouse_in_handle = False
        self.range = range if range != None else [0, 100, 1]
        self.value = 0
        self.selected = False
        super().__init__(list, x, y, width, height, uid=uid,color=color,
        camera=camera,border=border,border_color=border_color,
        border_radius=border_radius)
        self.slide_rect = pygame.rect.Rect(20, 0, width - 40, height//2.5)
        self.handle = pygame.rect.Rect(0, 0, 10, height-10)
        self.slide_rect.centery = height // 2
        self.handle.centery = height // 2
        self.text_panel = None

        if text:
            self.text_panel = TextBox(
                None, 10, 0, width, height, text=text,font=font, align="left", color=(0, 0, 0, 0)
            )
            self.slide_rect.w -= self.text_panel.text_rect.w + 10
            self.slide_rect.x += self.text_panel.text_rect.w + 10
        self.handle.centerx = self.slide_rect.x
        self.draw()
        # self.image.set_alpha(255)

    def set_text(self, text):
        if not self.text_panel:
            return
        self.text_panel.set_text(text)
        self.text_panel.draw()
        self.draw()

    def click(self):
        if self.func:
            self.func()
        self.feedback = 10
        self.draw()

    def mouse_enter(self):
        self.draw()

    def mouse_leave(self):
        self.draw()

    def enable(self):
        self.disabled = False
        self.draw()

    def disable(self):
        self.disabled = True
        self.draw()

    def set_value(self, value):
        if value == self.value:
            return
        if value < 0 or value > 1:
            return
        self.value = value
        self.handle.centerx = self.slide_rect.left + self.slide_rect.w * value
        if self.func:
            self.func(value)
        self.draw()

    def get_value(self):
        return self.value

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed):
        super().update(dt, mouse_pos, mouse_button, mouse_pressed)

        if self.mouse_in:
            if not self.mouse_in_handle and self.handle.move(
                *self.rect.topleft
            ).collidepoint(mouse_pos):
                self.mouse_in_handle = True
                self.draw()

            if self.mouse_in_handle and not self.handle.move(
                *self.rect.topleft
            ).collidepoint(mouse_pos):
                self.mouse_in_handle = False
                self.draw()
            if mouse_button[1]:
                self.set_pos_to_mouse(mouse_pos[0])
                self.selected = True
        else:
            if self.mouse_in_handle:
                self.mouse_in_handle = False
        if self.selected:
            # print(mouse_pressed)
            if not mouse_pressed[0]:
                self.selected = False
                self.draw()
            else:
                # print(mouse_pressed)
                self.set_pos_to_mouse(mouse_pos[0])

    def set_pos_to_mouse(self, pos):
        new_pos = pos - self.rect.x
        if new_pos < self.slide_rect.left:
            new_pos = self.slide_rect.left
        elif new_pos > self.slide_rect.right:
            new_pos = self.slide_rect.right
        new_pos = (new_pos - self.slide_rect.x) / self.slide_rect.w
        # print(new_pos)
        self.set_value(new_pos)

    def draw(self):

        super().draw()
        if self.text_panel:
            self.image.blit(self.text_panel.image, self.text_panel.rect)
        pygame.draw.rect(
            self.image,lib.sky_blue,
            (
                *self.slide_rect.topleft,
                self.handle.right-self.slide_rect.x,self.slide_rect.h
            ),
            0,5
        )
        pygame.draw.rect(self.image, lib.dark_gray, self.slide_rect, 2,5)
        pygame.draw.rect(self.image, lib.river_blue, self.handle,0,0)
        if self.mouse_in_handle or self.selected:
            pygame.draw.rect(self.image, lib.silver, self.handle, 2,0)
