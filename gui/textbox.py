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
        text=None,
        font=lib.default_text_size,
        color=[50, 50, 50],
        text_color=lib.cloud_white,
        align="center",
        uid="",
        border_radius=0,
        border=0,
        border_color=[50, 50, 50],
        camera=None,
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
            camera=camera,
        )
        self.color = color
        self.text_color = text_color
        self.font = font
        self.align = align if align in ["center", "left", "right"] else "center"
        self.text = text
        self.padding = 5
        self.text_rect = None
        self.set_text(text, color=color, text_color=text_color)

    def set_text(self, text, color=None, text_color=None):
        if color:
            super().set_color(color)
        if text_color:
            self.text_color = text_color
        self.text = text
        if self.text:
            self.text_surf = lib.render_text(self.text, self.font, self.text_color)
            self.text_rect = self.text_surf.get_rect()
            self.text_rect.centery = self.rect.h // 2
            if self.align == "center":
                self.text_rect.centerx = self.rect.w // 2
            elif self.align == "left":
                self.text_rect.left = 0 + self.padding
            elif self.align == "right":
                self.text_rect.right = self.rect.w - self.padding
        self.draw()

    def get_text(self):
        return self.text

    def draw(self):
        super().draw()
        if not self.text:
            return
        self.image.blit(self.text_surf, self.text_rect)
