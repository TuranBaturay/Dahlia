import pygame
import lib as lib
from debugger import Debugger
import gui as gui

if not __name__ == "__main__":
    exit()

pygame.init()
screen = pygame.display.set_mode((lib.WIDTH, lib.HEIGHT))
clock = pygame.time.Clock()


class OptionFrame(gui.Panel):
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
        text="",
    ) -> None:
        super().__init__(
            gui_list,
            x,
            y,
            width,
            height,
            color,
            border,
            border_color,
            border_radius,
            uid,
        )
        self.button = gui.Button(
            gui_list, 0, 0, 30, 30, "x", color=lib.dark_blue, border_radius=10
        )
        self.label = gui.TextBox(
            gui_list, 0, 0, width, 30, text, color=lib.wet_blue, border_radius=10
        )
        self.button.set_func(
            lambda: [
                gui_list.remove(self),
                gui_list.remove(self.button),
                gui_list.remove(self.label),
            ]
        )
        self.mouse_offset = (0, 0)
        self.move = False
        self.set_pos((x, y))

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed):
        super().update(dt, mouse_pos, mouse_button, mouse_pressed)
        if self.visible and mouse_button[3] and self.mouse_in:
            self.mouse_offset = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            self.move = True
        if self.visible and self.move:
            self.set_pos(mouse_pos)
        if self.move and not mouse_pressed[2]:
            self.move = False

    def set_pos(self, pos):
        self.rect.topleft = (
            pos[0] - self.mouse_offset[0],
            pos[1] - self.mouse_offset[1],
        )
        self.button.rect.bottomleft = self.rect.topright
        self.label.rect.bottomleft = self.rect.topleft

    def draw(self):
        super().draw()


class SelectionFrame(gui.Panel):
    def __init__(
        self,
        surface=None,
        list=None,
        x=0,
        y=0,
        width=100,
        height=100,
        color=None,
        border=0,
        border_color=lib.dark_gray,
        border_radius=0,
        uid="",
        image=None,
    ) -> None:
        super().__init__(
            list, x, y, width, height, color, border, border_color, border_radius, uid
        )
        self.fixed = False
        self.set_up = False
        self.surface = surface
        self.source = (0, 0)
        self.hide()

    def update(self, dt, mouse_pos, mouse_button, mouse_pressed=None):
        super().update(dt, mouse_pos, mouse_button, mouse_pressed)
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
                self.rect.x = mouse_pos[0]
                self.rect.w = self.source[0] - mouse_pos[0]
            else:
                self.rect.w = mouse_pos[0] - self.source[0]
                self.rect.x = self.source[0]
            if mouse_pos[1] < self.source[1]:
                self.rect.y = mouse_pos[1]
                self.rect.h = self.source[1] - mouse_pos[1]
            else:
                self.rect.h = mouse_pos[1] - self.source[1]
                self.rect.y = self.source[1]

    def draw(self):
        if self.border:
            pygame.draw.rect(
                self.surface,
                self.border_color,
                self.rect,
                self.border,
                self.border_radius,
            )


debugger = Debugger(screen)
gui_list = []
image = pygame.image.load("Assets/sprites/sprites.png").convert_alpha()
sf = SelectionFrame(screen, None, 0, 0, 100, 100, border=3, border_color=lib.sky_blue)
mode = "main"
loop = True
while loop:
    dt = clock.tick(60) / 1000
    mouse_button = {1: False, 2: False, 3: False, 4: False, 5: False}
    debugger.set("FPS", str(int(clock.get_fps())), True)
    screen.fill((20, 7, 15))

    screen.blit(image, (0, 0))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            loop = False
        if event.type == lib.INPUTBOX:
            if event.key == "ON":
                mode = "input"
                pygame.key.set_repeat(300, 20)

            else:
                mode = "main"
                pygame.key.set_repeat()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in mouse_button.keys():
            mouse_button[event.button] = True
        if event.type == pygame.KEYDOWN:
            if mode == "input":
                if event.mod & pygame.KMOD_SHIFT or event.mod & pygame.KMOD_CAPS:
                    caps = True
                else:
                    caps = False
            elif event.key == pygame.K_s:
                if sf.visible:
                    OptionFrame(
                        gui_list, *sf.rect, border=3, text="LABEL", color=[0, 0, 0, 0]
                    )
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
    if mode == "input":
        if sf.visible:
            sf.draw()

    if mode == "main":
        for panel in gui_list:
            panel.update(
                dt, pygame.mouse.get_pos(), mouse_button, pygame.mouse.get_pressed()
            )
            if panel.visible:
                screen.blit(panel.image, panel.rect)
        sf.update(dt, pygame.mouse.get_pos(), mouse_button, pygame.mouse.get_pressed())
        if sf.visible:
            sf.draw()
    debugger.update()
    pygame.display.flip()

pygame.quit()
