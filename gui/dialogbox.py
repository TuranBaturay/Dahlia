from .panel import Panel
from .textbox import TextBox
import lib as lib
import pygame


class DialogBox(TextBox):
    def __init__(
        self,
        gui_list,
        x,
        y,
        width,
        height,
        text="",
        text_color=lib.cloud_white,
        font=lib.default_text_size,
        color=[50, 50, 50],
        align="center",
        padding=5,
        uid="",
        border_radius=0,
        border=0,
        border_color=[50, 50, 50],
        camera=None,
    ):
        self.text_width = width - padding * 2

        super().__init__(
            gui_list,
            x,
            y,
            width,
            height,
            "",
            font,
            color,
            text_color,
            align,
            uid=uid,
            border_radius=border_radius,
            border=border,
            border_color=border_color,
            camera=camera,
        )
        self.color = color
        self.font = font
        self.align = align
        self.padding = padding
        self.text_rect = pygame.Rect(padding, padding, 0, 0)
        self.text = text
        self.text_list = []
        self.default_text_color = self.text_color
        self.last_pos = (0, 0)
        self.color_list = []

        self.set_text(text, color)
        self.clear_text()

    def set_default_text_color(self, color):
        if isinstance(color, str):
            color = getattr(lib, color, None)
        if color:
            self.default_text_color = color

    # [{'blabla'},{'blabla blabla'},{'blablala'}]

    def split_line_list(self, line):

        color_part_index = 0

        while (
            lib.get_text_size(
                "".join(part["text"] for part in line[: color_part_index + 1]),
                self.font,
            )[0]
            < self.text_width
        ):
            color_part_index += 1

        relative_letter_index = 0
        while (
            lib.get_text_size(
                "".join(part["text"] for part in line[:color_part_index])
                + line[color_part_index]["text"][:relative_letter_index],
                self.font,
            )[0]
            < self.text_width
        ):
            relative_letter_index += 1
        relative_letter_index -= 1

        # i = split index in the joined text
        # print(line[:color_part_index+1])
        if (any(" " in k["text"] for k in line[:color_part_index])) or (
            " " in line[color_part_index]["text"][: relative_letter_index + 1]
        ):
            while line[color_part_index]["text"][relative_letter_index] != " ":
                relative_letter_index -= 1
                if relative_letter_index < 0:
                    color_part_index -= 1
                    relative_letter_index = len(line[color_part_index]["text"]) - 1

        left = line[:color_part_index]
        left.append(
            {
                "color": line[color_part_index]["color"],
                "text": line[color_part_index]["text"][:relative_letter_index],
            }
        )
        right = line[color_part_index + 1 :]
        right.insert(
            0,
            {
                "color": line[color_part_index]["color"],
                "text": line[color_part_index]["text"][relative_letter_index:],
            },
        )
        # print("split at : ",line[color_part_index]['text'][relative_letter_index]," of ",line[color_part_index]['text'])

        return left, right

    def process_text(self, text):
        i = 0
        line_w = 0
        self.text_list = []
        color_counter = 0
        tmp1 = text.split("\\n")
        tmp = []
        next_index = 0
        in_color_block = False
        for k, line in enumerate(tmp1):
            tmp.append([])
            while line:
                if in_color_block:
                    next_index = line.find("}")
                    if next_index == -1:
                        next_index = len(line)
                    part, rest = line[:next_index], line[next_index + 1 :]
                    split_part = part.split(maxsplit=1)
                    part = {"color": split_part[0], "text": "".join(split_part[1:])}
                    in_color_block = False
                else:
                    next_index = line.find("{")
                    if next_index == -1:
                        next_index = len(line)
                    part, rest = line[:next_index], line[next_index + 1 :]
                    part = {"color": self.default_text_color, "text": part}
                    in_color_block = True
                # print(part)
                line = rest
                if part:
                    tmp[k].append(part)
        length = len(tmp)
        while i < length:
            line = tmp[i]
            if not line:
                i += 1
                continue
            # print(line)
            line_w = lib.get_text_size(
                "".join([data["text"] for data in line]).rstrip(), self.font
            )[0]
            if line_w > self.text_width:
                line_w = 0
                left, right = self.split_line_list(line)
                # print("split line : ", left, "|", right)
                line = left
                if right:
                    if i + 1 < length:
                        tmp.insert(i + 1, right)
                    else:
                        tmp.append(right)
                    length += 1
            self.text_list.append(line)
            i += 1

    def set_text(self, text, color=None, text_color=None):
        if (
            text == self.text
            and color in [None, self.color]
            and text_color in [None, self.text_color]
        ):
            return

        self.text = text
        self.process_text(text)
        self.draw()

    def set_text_color(self, color):
        if isinstance(color, str):
            color = getattr(lib, color, None)
        if color:
            self.text_color = color

    def get_text(self):
        return super().get_text()

    def clear_text(self):
        self.text = ""
        self.text_list = [""]

        self.draw()

    def draw(self):
        Panel.draw(self)
        self.text_color = self.default_text_color
        topleft = (0, 0)
        color_index = 0
        for i in range(len(self.text_list)):
            # [["this is "],["a very important "],["text."]]
            line = self.text_list[i]

            self.text_surf = lib.render_text(
                "".join(color_part["text"] for color_part in line),
                self.font,
                self.text_color,
            )
            self.text_rect = self.text_surf.get_rect()

            self.text_rect.top = self.padding + (30 * i)

            if self.align == "center":
                self.text_rect.centerx = self.rect.w // 2
            elif self.align == "left":
                self.text_rect.left = 0 + self.padding
            elif self.align == "right":
                self.text_rect.right = self.rect.w - self.padding
            topleft = self.text_rect.topleft

            for color_part in line:
                self.set_text_color(color_part["color"])
                color_surf = lib.render_text(
                    color_part["text"], self.font, self.text_color
                )
                color_surf_rect = color_surf.get_rect()
                color_surf_rect.topleft = topleft
                topleft = color_surf_rect.topright

                self.image.blit(color_surf, color_surf_rect)
                # pygame.draw.rect(self.image, (200, 0, 200), color_surf_rect, 2)
                color_index += 1
            i += 1

            # pygame.draw.rect(self.image,(200,200,200),self.text_rect,3)
        self.last_pos = self.text_rect.midright
