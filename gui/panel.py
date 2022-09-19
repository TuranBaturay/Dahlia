import pygame
import lib as lib
from pygame.math import Vector2


class Panel(pygame.sprite.Sprite):
    def __init__(
        self,
        gui_list=None,
        x=0,
        y=0,
        width=100,
        height=100,
        color=lib.transparent,
        border=0,
        border_color=lib.dark_gray,
        border_radius=0,
        border_radii = [-1,-1,-1,-1],
        uid="",
        camera=None,
    ):
        pygame.sprite.Sprite.__init__(self)

        if gui_list != None:
            gui_list.append(self)
        self.image = pygame.surface.Surface((width, height), pygame.SRCALPHA)

        self.rect = pygame.rect.Rect(x, y, width, height)
        self.mouse_in = False
        self.mouse_pressed = [False, False, False]
        self.mouse_in_flag = False
        self.visible = True
        self.uid = uid
        self.color = color
        self.border = border
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_radii =border_radii
        self.origin = Vector2(x, y)
        if not self.color:
            self.color = (0, 0, 0)
        
        self.draw_rect_args = [self.image, self.color, (0, 0, width, height), 0,self.border_radius,*self.border_radii]
        self.draw_rect_args_border = [self.image, self.border_color, (0, 0, width, height), self.border,self.border_radius,*self.border_radii]


        pygame.draw.rect(*self.draw_rect_args)
        if self.border : pygame.draw.rect(*self.draw_rect_args_border)
        self.camera = camera

    def mouse_enter(self):
        pass


    def mouse_leave(self):
        pass

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_color(self,color):
        self.color = color
        self.draw_rect_args  = [self.image, color, (0, 0, *self.rect.size), 0,self.border_radius,*self.border_radii]

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed=None):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_in = True
            if not self.mouse_in_flag:
                self.mouse_in_flag = True
                self.mouse_pressed = mouse_pressed

                self.mouse_enter()
        else:
            self.mouse_in = False
            if self.mouse_in_flag:
                self.mouse_in_flag = False

                self.mouse_leave()

    def update_pos(self):

        if self.camera:
            self.rect.topleft = self.origin - self.camera.int_pos

    def draw(self):
        self.image.fill((0, 0, 0, 0))
        if self.camera:
            self.update_pos()
        pygame.draw.rect(*self.draw_rect_args)
        if self.border : pygame.draw.rect(*self.draw_rect_args_border)
