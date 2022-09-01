from .panel import Panel
from .textbox import TextBox
import lib as lib
import pygame


class DialogBox(TextBox):
    def __init__(
        self,
        list,
        x,
        y,
        width,
        height,
        text="",
        font=26,
        color=[50, 50, 50],
        align="center",
        padding=5,
        uid="",
        border_radius=0,
        border=0,
        border_color=[50,50,50]
    ):
        self.text_width = width - padding * 2

        super().__init__(
            list,
            x,
            y,
            width,
            height,
            "",
            font,
            color,
            align,
            uid=uid,
            border_radius=border_radius,
            border=border,
            border_color=border_color
        )
        self.color = color
        self.font = font
        self.align = align
        self.padding = padding
        self.text_rect = pygame.Rect(padding, padding, 0, 0)
        self.text = text
        self.text_list = []
        self.last_pos = (0, 0)

        self.set_text(text, color)
        self.clear_text()

    def process_text(self, text):
        i = 0
        line_w = 0
        self.text_list = []
        tmp = text.split("\n")
        length = len(tmp)
        while i < length:
            line = tmp[i]
            line_w = lib.get_text_size(line, self.font)[0]
            if line_w > self.text_width:
                line_w = 0
                for index, letter in enumerate(line):
                    line_w = lib.get_text_size(line[: index + 1], self.font)[0]
                    if line_w > self.text_width:
                        last_whitespace = line.rfind(" ", 0, index)
                        if last_whitespace == -1:
                            last_whitespace = index
                        else:
                            last_whitespace += 1
                        left, right = line[:last_whitespace], line[last_whitespace:]
                        right.lstrip(" ")
                        # print(left,"|",right)
                        line = left
                        tmp.insert(i + 1, right)
                        length += 1
                        break

            self.text_list.append(line)

            i += 1

    def set_text(self, text, color=None):
        if text == self.text and color in [None, self.color]:
            return
        if color:
            self.color = color
        self.text = text
        self.process_text(text)
        self.draw()

    def get_text(self):
        return super().get_text()

    def clear_text(self):
        self.text = ""
        self.text_list = [""]
        self.draw()

    def draw(self):
        Panel.draw(self)
        for i, line in enumerate(self.text_list):

            self.text_surf = lib.render_text(line, self.font, (200, 200, 200))
            self.text_rect = self.text_surf.get_rect()
            self.text_rect.top = self.padding + (30 * i)
            if self.align == "center":
                self.text_rect.centerx = self.rect.w // 2
            elif self.align == "left":
                self.text_rect.left = 0 + self.padding
            elif self.align == "right":
                self.text_rect.right = self.rect.w - self.padding
            self.image.blit(self.text_surf, self.text_rect)
            i += 1
            # pygame.draw.rect(self.image,(200,200,200),self.text_rect,3)
        self.last_pos = self.text_rect.midright
