from .panel import Panel
import lib as lib
import pygame


class Meter(Panel):
    def __init__(
        self,
        list=None,
        x=0,
        y=0,
        width=100,
        height=100,
        color=None,
        border=0,
        border_color=...,
        border_radius=10,
        max=100,
        value=100,
        bg_color=lib.darker_gray,
        uid="",
        camera=None,
    ):
        super().__init__(
            list,
            x,
            y,
            width,
            height,
            color,
            border,
            border_color,
            border_radius,
            uid=uid,
            camera=camera,
        )
        self.max = max
        self.value = max
        self.target_width = int(self.value * self.rect.w / self.max)
        self.meter_width = self.target_width
        self.color = color
        self.bg_color = bg_color
        self.border_radius = border_radius
        self.draw_rect = self.rect.copy()
        self.draw_rect.topleft = 0, 0
        self.meter_rect = self.draw_rect.copy()
        self.meter_rect.inflate_ip(-10, -10)
        self.max_meter_width = self.meter_rect.w
        self.set_value(value)
        self.draw()

    def set_value(self, value):
        # print(self.value,value)

        if value >= self.max:
            self.value = self.max
            self.target_width = self.max_meter_width
            return
        elif value <= 0:
            self.value = 0
            self.target_width = 0
            return
        if value == self.value:
            return
        self.value = value

        self.target_width = int(self.value * self.max_meter_width / self.max)

    def increase(self, value):
        self.set_value(self.value + value)

    def decrease(self, value):
        self.set_value(self.value - value)

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed=None):
        super().update(dt, mouse_pos, mouse_button, mouse_pressed)
        if self.meter_width != self.target_width:
            self.meter_width += (self.target_width - self.meter_width) / 10
            self.meter_rect.w = int(self.meter_width)
            self.draw()

    def draw(self):
        # super().draw()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.image, lib.cloud_white, self.draw_rect, 0, self.border_radius
        )

        pygame.draw.rect(self.image, self.color, self.draw_rect, 3, self.border_radius)

        pygame.draw.rect(self.image, self.color, self.meter_rect, 0, self.border_radius)
