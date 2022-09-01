from .panel import Panel
import lib as lib


class TextBox(Panel):
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
        uid="",
        border_radius=0,
        border=0,
        border_color=[50, 50, 50],
    ):
        super().__init__(
            list,
            x,
            y,
            width,
            height,
            color,
            uid=uid,
            border_radius=border_radius,
            border=border,
            border_color=border_color,
        )
        self.color = color
        self.font = font
        self.align = align
        self.text = text
        self.padding = 5
        self.text_rect = None
        self.set_text(text, color)

    def set_text(self, text, color=None):
        if color:
            self.color = color
        self.text = text
        self.draw()

    def get_text(self):
        return self.text

    def draw(self):
        super().draw()
        if not self.text:
            return
        self.text_surf = lib.render_text(self.text, self.font, (200, 200, 200))
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.centery = self.rect.h // 2
        if self.align == "center":
            self.text_rect.centerx = self.rect.w // 2
        elif self.align == "left":
            self.text_rect.left = 0 + self.padding
        elif self.align == "right":
            self.text_rect.right = self.rect.w - self.padding
        self.image.blit(self.text_surf, self.text_rect)
