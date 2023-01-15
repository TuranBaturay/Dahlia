from time import strftime
from .mode import Mode
from main import App
import gui as gui
import lib as lib
import pygame
import os
import datetime as datetime


class LevelViewer(Mode):
    def __init__(self, app: App, display) -> None:
        self.ti = app.get_input()
        self.refresh = pygame.image.load("Assets/icons/refresh.png").convert_alpha()
        super().__init__(app, display)
        self.select_level("level")
        
    def init_gui(self):
        self.gui_list = []

        panel = gui.Panel(
            self.gui_list,
            50,
            50,
            lib.WIDTH - 100,
            lib.HEIGHT - 100,
            lib.dark_blue,
            border_radius=10,
        )
        title = gui.TextBox(
            self.gui_list,
            *panel.rect.topleft,
            panel.rect.w,
            30,
            text="Levels",
            color=lib.wet_blue,
            border_radius=10,
        )
        gui.Button(
            self.gui_list,
            *title.rect.topleft,
            60,
            30,
            "<",
            func=lambda: self.app.set_mode("title"),
            color=lib.wet_blue,
            border_radius=10,
        )

        left = gui.Panel(
            self.gui_list,
            panel.rect.x + 20,
            panel.rect.y + 70,
            panel.rect.w // 2 - 40,
            panel.rect.h - 100,
            color=[0, 0, 0, 0],
            border_color=lib.wet_blue,
            border=4,
            border_radius=5,
        )
        right = gui.Panel(
            self.gui_list,
            panel.rect.x + 40 + panel.rect.w // 2 - 40,
            panel.rect.y + 70,
            panel.rect.w // 2 - 20,
            panel.rect.h - 100,
            color=[0, 0, 0, 0],
            border_color=lib.wet_blue,
            border=4,
            border_radius=5,
        )

        refresh_button = gui.Button(
            self.gui_list,
            left.rect.right - 40,
            left.rect.y + 10,
            30,
            30,
            image=self.refresh,
            func=self.init_gui,
            color=lib.dark_turquoise,
            border_radius=10,
        )

        new = gui.Button(
            self.gui_list,
            refresh_button.rect.left - 40,
            left.rect.y + 10,
            30,
            30,
            text="+",
            color=lib.dark_turquoise,
            border_radius=10,
        )

        new.set_func(
            lambda: self.ti.ask_text_input(
                lambda text: self.add_level(text) if text else None,
                400,
                200,
                "Level Name",
                20,
                False,
            )
        )
        thumbnail = gui.Panel(
            self.gui_list,
            0,
            right.rect.y + 20,
            1080 // 2,
            600 // 2,
            lib.cloud_white,
            uid="thumbnail",
            border=3,
            border_color=lib.wet_blue,
        )
        thumbnail.rect.centerx = right.rect.centerx
        # thumbnail.image.blit()
        gui.TextBox(
            self.gui_list,
            thumbnail.rect.x,
            thumbnail.rect.bottom + 10,
            thumbnail.rect.w,
            30,
            "",
            font=12,
            uid="level_name",
            color=lib.wet_blue,
            border_radius=10,
        )

        self.last_modified = gui.TextBox(
            self.gui_list,
            thumbnail.rect.x,
            thumbnail.rect.bottom + 60,
            320,
            30,
            text="",
            font=12,
            color=lib.dark_blue,
            border=3,
            border_color=lib.wet_blue,
            border_radius=10,
        )

        play = gui.Button(
            self.gui_list,
            right.rect.centerx - 90,
            right.rect.bottom - 50,
            70,
            30,
            "Play",
            font=12,
            uid="play_button",
            color=lib.dark_turquoise,
            border_radius=10,
        )
        play.rect.centerx = right.rect.centerx
        gui.Button(
            self.gui_list,
            play.rect.left - 80,
            right.rect.bottom - 50,
            70,
            30,
            "Edit",
            font=12,
            uid="edit_button",
            color=lib.wet_blue,
            border_radius=10,
        )
        gui.Button(
            self.gui_list,
            play.rect.right + 10,
            right.rect.bottom - 50,
            70,
            30,
            "Delete",
            font=12,
            uid="remove_button",
            color=lib.darker_red,
            border_radius=10,
        )
        self.level_list = sorted(lib.get_files_in_dir("levels", ".json"))
        row = 0
        column = 0
        for level in self.level_list:
            level_name = os.path.basename(level).split(".")[0]
            gui.Button(
                self.gui_list,
                left.rect.x + 20 + (170 * column),
                left.rect.y + 50 + (50 * row),
                160,
                30,
                text=level_name,
                font=12,
                color=lib.wet_blue,
                uid="level_button",
                func=lambda level_name=level_name: self.select_level(level_name),
                border_radius=10,
            )
            row += 1
            if left.rect.y + 50 + (50 * row) + 30 > left.rect.bottom - 10:
                row = 0
                column += 1
        self.select_level(self.app.selected_level)

    def select_level(self, level_name):
        for button in lib.get_by_id(self.gui_list, "level_button"):
            # print(button.get_text(),level_name)
            if button.get_text() == level_name:
                button.set_color(lib.dark_turquoise)
                self.app.selected_level = level_name
            else:
                button.set_color(lib.wet_blue)
        name_label = lib.get_by_id(self.gui_list, "level_name")[0]
        name_label.set_text(level_name)

        remove_button = lib.get_by_id(self.gui_list, "remove_button")[0]
        remove_button.set_func(
            lambda: self.ti.ask_yesno(
                # lambda text,level_name=level_name: self.remove_level(level_name) if (text!=None and text.lower()=="yes") else print(text),
                lambda value: self.remove_level(level_name)
                if value
                else None,
                f"Delete '{level_name}' ?",
            )
        )

        thumbnail = lib.get_by_id(self.gui_list, "thumbnail")[0]

        play_button = lib.get_by_id(self.gui_list, "play_button")[0]
        play_button.set_func(lambda: [self.load_level(level_name, skip_vignette=True)])
        edit_button = lib.get_by_id(self.gui_list, "edit_button")[0]
        edit_button.set_func(
            lambda: [self.load_level(level_name, "edit", skip_vignette=True)]
        )
        # print(play_button)
        mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(f"levels/{level_name}.json")
        )
        self.last_modified.set_text(
            "Last modified : " + mtime.strftime("%m/%d/%Y, %H:%M:%S")
        )

        level_surf = lib.level_to_pixel(
            lib.load_data(lib.level_path + level_name + ".json")
        )
        new_width = level_surf.get_width() * 2
        scaled = pygame.surface.Surface((new_width, new_width), pygame.SRCALPHA)
        pygame.transform.scale(level_surf, (new_width, new_width), scaled)
        thumbnail.draw()
        thumbnail.image.blit(scaled, (10, 10))

        # print(name_field)

    def load_level(self, level_name, mode="game", skip_vignette=False):

        self.app.load_level(level_name, mode, skip_vignette=skip_vignette)

    def remove_level(self, level_name):
        self.app.remove_level(level_name)
        self.app.selected_level = os.path.basename(self.level_list[0]).split(".")[0]
        self.init_gui()

    def add_level(self, name):
        if name == "":
            return
        if name in [os.path.basename(level).split(".")[0] for level in self.level_list]:
            return
        self.app.level.__init__(self.display, self.app)
        if self.app.save_level(name):
            self.init_gui()
            self.select_level(name)

    def enter_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp,(0,0))
        self.glide_in_update(dt, mouse, mouse_button, mouse_pressed)

    def on_exit_mode(self, exit_event):
        return super().on_exit_mode_glide_out(exit_event)
    def exit_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.blit(self.app.display_stamp,(0,0))
        return super().glide_out_update(dt, mouse, mouse_button, mouse_pressed)
    def on_enter_mode(self,bool:skip = False):
        self.init_gui()
        if skip:
            super().on_enter_mode()
            return
        self.on_enter_mode_glide_in()
