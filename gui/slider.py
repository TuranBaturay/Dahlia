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
        func=None,
        range=None,
        color=lib.wet_blue,
        uid="",
    ):
        self.text_panel = None
        self.disabled = False
        self.func = func
        self.mouse_in_flag = False
        self.mouse_in_handle = False
        self.range = range if range != None else [0, 100, 1]
        self.value = 0
        self.selected = False
        self.color = color
        super().__init__(list, x, y, width, height, uid=uid)
        self.slide_rect = pygame.rect.Rect(20, 0, width - 40, 10)
        self.handle = pygame.rect.Rect(0, 0, 10, 30)
        self.slide_rect.centery = height // 2
        self.handle.centery = height // 2
        if text:
            self.text_panel = TextBox(
                None, 0, 0, width, height, text=text, align="left", color=color
            )
            self.slide_rect.w -= self.text_panel.text_rect.w
            self.slide_rect.x += self.text_panel.text_rect.w
        self.handle.centerx = self.slide_rect.x
        self.draw()
        # self.image.set_alpha(255)

    def set_text(self, text):
        if not self.text_panel:
            return
        self.text_panel.set_text(text)
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
            elif self.mouse_in:
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

        self.image.fill(self.color)
        if self.text_panel:
            self.text_panel.draw()
            self.image.blit(self.text_panel.image, (0, 0))
        pygame.draw.rect(self.image, lib.dark_gray, self.slide_rect, 2)
        # pygame.draw.rect(self.image,(200,180,200,200),self.slide_rect,4)

        pygame.draw.rect(self.image, lib.river_blue, self.handle)
        if self.mouse_in_handle or self.selected:
            # print("Handle")
            pygame.draw.rect(self.image, lib.silver, self.handle, 2)
