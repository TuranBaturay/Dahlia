from .mode import Mode
import gui as gui
import lib as lib
from pygame.locals import *
from pygame.math import Vector2
import pygame
from tile import Tile
from math import cos,ceil


class Edit(Mode):
    
    def __init__(self, app, display) -> None:
        self.eye_open = pygame.image.load("Assets/icons/eye_open.png").convert_alpha()
        self.eye_close = pygame.image.load("Assets/icons/eye_close.png").convert_alpha()

        self.up_triangle = pygame.Surface((30, 30))
        self.up_triangle.set_colorkey((0, 0, 0))
        self.gear_image = pygame.image.load("Assets/icons/gear.png").convert_alpha()
        pygame.draw.polygon(
            self.up_triangle, lib.cloud_white, [(15, 10), (10, 20), (20, 20)]
        )
        self.down_triangle = pygame.transform.flip(self.up_triangle, False, True)
        self.brush_image = pygame.image.load("Assets/icons/brush.png").convert_alpha()
        self.select_image = pygame.image.load("Assets/icons/select.png").convert_alpha()
        self.tileset_list = ["animated", "static"]
        self.current_tileset = "static"
        self.pages = {"animated": 0, "static": 0}
        self.selected_tiles = {"animated": 0, "static": 0}
        self.camera_target = Vector2(0, 0)
        self.preview_tile = Tile((0, 0))
        self.preview_tile_img = lib.tileset_get(0)
        self.hovered_tile = None
        self.preview_border = pygame.Rect(0, 0, 64, 64)
        self.current_layer = None
        self.text_input = app.get_input()
        self.show_single = False
        self.tools = ["brush", "select", "spawn"]
        self.tool_images = {
            "brush": self.brush_image,
            "select": self.select_image,
            "spawn": None,
        }
        self.tool_text = {"brush": "B", "select": "Sel", "spawn": "S"}
        self.tool_buttons = {}
        self.tool = "brush"
        self.saved = True
        self.shift_key = False
        self.previous_state = None

        self.camera_vel = Vector2(0,0)
        self.camera_speed = 600

        #spawn indicator
        self.spawn_offset = Vector2(32, 32)
        self.spawn_indicator = pygame.Surface((64, 64), pygame.SRCALPHA)
        s = lib.render_text("SPAWN", lib.small_font, lib.cloud_white)
        r = s.get_rect()
        r.center = (32, 32)
        self.spawn_indicator.blit(s, r)
        self.set_tool("brush")

        super().__init__(app, display)


    def init_gui(self):
        self.tool_buttons = {}

        def release_sf(self: gui.SelectionFrame):
            self.origin[0] = round(self.origin[0] / 64) * 64
            self.origin[1] = round(self.origin[1] / 64) * 64
            self.rect.w = ceil(self.rect.w / 64) * 64
            self.rect.h = ceil(self.rect.h // 64) * 64
            self.rect.topleft = self.origin

        self.gui_list = []
        self.app.level = self.app.level
        self.sf = gui.SelectionFrame(
            None,
            width=0,
            height=0,
            color=[0, 0, 0, 0],
            border=3,
            border_color=lib.sky_blue,
            camera=self.app.camera,
            border_radius=0,
        )
        self.sf.on_release = release_sf
        self.main_panel = gui.Panel(
            self.gui_list, 0, 0, 400, lib.HEIGHT, lib.dark_blue, 3, lib.wet_blue,10, [0,0,10,10]
        )

        gui.Button(
            self.gui_list,
            20,
            10,
            30,
            30,
            "<",
            func=lambda: self.app.set_mode("game"),
            color=lib.wet_blue,
            border_radius=10,
        )
        gui.Button(
            self.gui_list,
            60,
            10,
            30,
            30,
            image=self.gear_image,
            color=lib.wet_blue,
            border_radius=10,
            func=lambda: self.app.set_mode("settings"),
        )
        self.save_button = gui.Button(
            self.gui_list,
            self.main_panel.rect.w - 90,
            10,
            70,
            30,
            "Save",
            font=12,
            func=lambda: [
                self.app.save_level(self.app.selected_level),
                self.save_button.set_text("Save"),
                self.save_button.set_color(lib.darker_turquoise),
            ],
            color=lib.darker_turquoise,
            border_radius=10,
        )
        self.undo_button = gui.Button(
            self.gui_list,
            *self.save_button.rect.move(-80, 0).topleft,
            70,
            30,
            "Undo",
            font=12,
            func=self.load_state,
            color=lib.dark_turquoise,
            border_radius=10,
        )
        tool_panel = gui.Panel(
            self.gui_list,
            20,
            50,
            self.main_panel.rect.w - 40,
            100,
            color=[0, 0, 0, 0],
            border=3,
            border_color=lib.wet_blue,
            border_radius=10,
        )
        for x, tool in enumerate(self.tools):
            button = gui.Button(
                self.gui_list,
                tool_panel.rect.x + 10 + 40 * x,
                tool_panel.rect.y + 10,
                30,
                30,
                image=self.tool_images[tool],
                text=self.tool_text[tool] if not self.tool_images[tool] else None,
                color=lib.dark_turquoise if tool == self.tool else lib.wet_blue,
                border_radius=10,
                uid="tool_button",
            )
            self.tool_buttons[tool] = button
            button.set_func(lambda tool=tool: self.set_tool(tool))
        selector = gui.Panel(
            self.gui_list,
            20,
            tool_panel.rect.bottom + 40,
            self.main_panel.rect.w - 40,
            180,
            color=lib.dark_blue,
            border_color=lib.wet_blue,
            border=3,
            border_radius=10,
        )

        self.tileset_label = gui.TextBox(
            self.gui_list,
            *selector.rect.topleft,
            selector.rect.w,
            30,
            self.current_tileset,
            font=12,
            color=lib.wet_blue,
            border_radius=10,
        )

        self.tileset_label.rect.bottom = selector.rect.top + 10

        gui.Button(
            self.gui_list,
            self.tileset_label.rect.right - 30,
            self.tileset_label.rect.top,
            30,
            30,
            ">",
            color=lib.wet_blue,
            border_radius=10,
            func=self.switch_tileset,
        )
        page_button_panel = gui.Panel(
            self.gui_list,
            selector.rect.right - 50,
            0,
            40,
            120,
            color=lib.dark_blue,
            border=2,
            border_radius=10,
            border_color=lib.wet_blue,
        )

        page_button_panel.rect.centery = selector.rect.centery

        self.page_num = gui.TextBox(
            self.gui_list,
            *page_button_panel.rect.topleft,
            30,
            30,
            text="1",
            font=12,
            color=lib.wet_blue,
            border_radius=10,
        )

        self.page_button_up = gui.Button(
            self.gui_list,
            *page_button_panel.rect.topleft,
            30,
            30,
            image=self.up_triangle,
            color=lib.wet_blue,
            border_radius=10,
            func=lambda: self.set_page(self.pages[self.current_tileset] - 1),
        )
        self.page_button_up.rect.move_ip(5, 5)
        self.page_button_down = gui.Button(
            self.gui_list,
            *page_button_panel.rect.topleft,
            30,
            30,
            image=self.down_triangle,
            color=lib.wet_blue,
            border_radius=10,
            func=lambda: self.set_page(self.pages[self.current_tileset] + 1),
        )
        self.inspector_button = gui.Button(
            self.gui_list,
            0,
            0,
            30,
            30,
            "i",
            font=12,
            border_radius=10,
            color=lib.dark_blue,
            border=2,
            border_color=lib.light_blue,
            func=self.inspect,
        )
        self.remove_selection_button = gui.Button(
            self.gui_list,
            0,
            0,
            30,
            30,
            "x",
            font=12,
            border_radius=10,
            color=lib.darker_red,
            border=2,
            border_color=lib.dark_red,
            func=self.remove_selection,
        )
        self.inspector_button.hide()
        self.remove_selection_button.hide()
        self.page_button_down.rect.move_ip(5, 5)
        self.page_num.rect.move_ip(5, 5)

        self.page_num.rect.move_ip(0, 40)
        self.page_button_down.rect.move_ip(0, 80)

        for y in range(2):
            for x in range(4):
                gui.Button(
                    self.gui_list,
                    selector.rect.x + 25 + 70 * x,
                    selector.rect.y + 25 + 70 * y,
                    64,
                    64,
                    color=[0, 0, 0, 0],
                    uid="tile_button",
                )
        toggle = gui.Toggle(
            self.gui_list,
            selector.rect.x,
            selector.rect.bottom + 20,
            360,
            30,
            "Collision",
            font=12,
            func=lambda value: self.toggle_collision(value),
            color=lib.wet_blue,
            border_radius=10,
        )

        self.layer_selector = gui.Panel(
            self.gui_list,
            20,
            120,
            360,
            240,
            color=lib.dark_blue,
            border=3,
            border_color=lib.wet_blue,
            border_radius=10,
        )
        self.layer_selector.rect.top = toggle.rect.bottom + 30
        self.layer_selector_label = gui.TextBox(
            self.gui_list,
            *self.layer_selector.rect.topleft,
            360,
            30,
            "LAYERS",
            font=12,
            border_radius=10,
            color=lib.wet_blue,
        )
        self.add_layer_button = gui.Button(
            self.gui_list,
            self.layer_selector_label.rect.right - 30,
            self.layer_selector.rect.top,
            30,
            30,
            "+",
            font=12,
            color=lib.dark_turquoise,
            border_radius=10,
            border=3,
            border_color=lib.wet_blue,
            func=lambda: self.text_input.ask_text_input(
                lambda text: [self.add_layer(text), self.update_layer_selector()],
                400,
                200,
                "New layer",
            ),
        )
        self.update_layer_selector()
        self.set_page(self.pages[self.current_tileset])

    def save_state(self):
        self.previous_state = self.app.level.format()

    def load_state(self):
        if not self.previous_state:
            return
        tmp = self.app.level.format()
        self.app.level.load(self.previous_state)
        self.update_layer_selector()
        self.previous_state = tmp

    def modify(self):
        self.save_state()
        self.saved = False
        self.save_button.set_text("Save*")
        self.save_button.set_color(lib.dark_turquoise)

    def set_tool(self, tool):
        #print(tool)
        if not tool in self.tools:
            return
        self.tool = tool
        for t, b in self.tool_buttons.items():
            if t == tool:
                b.set_color(lib.dark_turquoise)
            else:
                b.set_color(lib.wet_blue)

    def inspect(self):
        tiles = self.get_selection_tiles()[0]
        if not tiles:
            return
        self.app.get_inspector().select_tile(tiles)

    def remove_selection(self):
        if self.sf.visible and self.sf.rect.size:
            self.modify()
            for tile in self.get_selection_tiles():
                # print("removing :",tile,tile.rect.x//64,tile.rect.y//64)
                self.app.level.remove(
                    tile.rect.x // 64, tile.rect.y // 64, self.current_layer
                )

    def toggle_collision(self, value):
        self.preview_tile.collision = value

    def update_layer_selector(self):
        self.gui_list = [
            panel
            for panel in self.gui_list
            if panel.uid not in ["layer_button", "layer_label"]
        ]
        self.layer_labels = []
        x_source = self.layer_selector.rect.x + 10
        max_len = len(self.app.level.layers)
        if max_len > 4:
            self.add_layer_button.disable()
        else:
            self.add_layer_button.enable()
        counter = max_len - 1
        for i, layer in enumerate(reversed(self.app.level.layers)):
            y_pos = self.layer_selector_label.rect.bottom + 10 + i * 40
            x_pos = x_source
            label = gui.Button(
                self.gui_list,
                x_pos,
                y_pos,
                190,
                30,
                layer[0],
                font=12,
                color=lib.dark_turquoise
                if self.current_layer == layer[0]
                else lib.wet_blue,
                uid="layer_label",
                align="left",
                border_radius=10,
                func=lambda layer=layer: self.set_layer(layer[0]),
            )
            label.set_right_click_func(
                lambda layer=layer: self.text_input.ask_text_input(
                    lambda text, layer=layer: [
                        self.rename_layer(layer[0], text),
                        self.update_layer_selector(),
                    ]
                    if text
                    else None,
                    400,
                    200,
                    "Rename layer",
                    25,
                )
            )
            x_pos += 200
            swap_up = gui.Button(
                self.gui_list,
                x_pos,
                y_pos,
                30,
                30,
                image=self.up_triangle,
                border_radius=10,
                color=lib.wet_blue,
                uid="layer_button",
                func=lambda counter=counter: [
                    self.swap_layers(counter + 1, counter),
                    self.update_layer_selector(),
                    # print(counter),
                ],
            )
            if i == 0:
                swap_up.disable()
            x_pos += 35

            swap_down = gui.Button(
                self.gui_list,
                x_pos,
                y_pos,
                30,
                30,
                image=self.down_triangle,
                border_radius=10,
                color=lib.wet_blue,
                uid="layer_button",
                func=lambda counter=counter: [
                    self.swap_layers(counter, counter - 1),
                    self.update_layer_selector(),
                    # print(counter),
                ],
            )
            if i == max_len - 1:
                swap_down.disable()
            x_pos += 35

            show_button = gui.Button(
                self.gui_list,
                x_pos,
                y_pos,
                30,
                30,
                border_radius=10,
                image=self.eye_open if layer[1].visible else self.eye_close,
                color=lib.wet_blue,
                uid="layer_button",
            )
            show_button.set_func(
                lambda layer=layer, show_button=show_button: [
                    layer[1].toggle_visibility(),
                    show_button.set_img(
                        self.eye_open if layer[1].visible else self.eye_close
                    ),
                ]
            )

            x_pos += 35
            remove_button = gui.Button(
                self.gui_list,
                x_pos,
                y_pos,
                30,
                30,
                "x",
                font=12,
                color=lib.darker_red,
                border_radius=10,
                uid="layer_button",
                func=lambda layer=layer: self.text_input.ask_text_input(
                    lambda text, layer=layer: self.remove_layer(layer[0])
                    if text and text.lower() in ["yes", "y"]
                    else None,
                    400,
                    200,
                    f"Remove '{layer[0]}' ? (yes/no)",
                    5,
                ),
            )
            if max_len == 1:
                remove_button.disable()
            counter -= 1

    def update_selector(self):
        tileset = (
            lib.animated_tileset_cache
            if self.current_tileset == "animated"
            else lib.tileset_cache
        )

        max_len = len(tileset)
        for x, tile_button in enumerate(lib.get_by_id(self.gui_list, "tile_button")):
            if x + 8 * self.pages[self.current_tileset] >= max_len:
                tile_button.set_img(None)
                tile_button.set_func(None)
                # tile_button.set_color(lib.darker_blue)

            elif self.current_tileset == "static":
                tile_button.set_img(lib.tileset_get(x + 8 * self.pages["static"]))
                tile_button.set_func(
                    lambda x=x: self.select_tile(x + 8 * self.pages["static"])
                )
            else:
                # print(x+8*self.pages["animated"],max_len)
                tile_button.set_img(
                    lib.animated_tileset_get(x + 8 * self.pages["animated"], 0)
                )
                tile_button.set_func(
                    lambda x=x: self.select_tile(x + 8 * self.pages["animated"])
                )

    def switch_tileset(self):
        index = self.tileset_list.index(self.current_tileset)
        index += 1
        if index >= len(self.tileset_list):
            index = 0
        self.current_tileset = self.tileset_list[index]
        # print(self.current_tileset)
        self.tileset_label.set_text(self.current_tileset)
        self.set_page(self.pages[self.current_tileset])
        self.select_tile(self.selected_tiles[self.current_tileset])
        self.update_selector()

    def select_tile(self, index):
        # print(index)
        self.selected_tiles[self.current_tileset] = index
        if self.current_tileset == "animated":
            self.preview_tile.set(
                {
                    "index": index,
                    "collision": self.preview_tile.collision,
                    "flip": self.preview_tile.flip,
                    "animated":True
                }
            )
            self.preview_tile_img = lib.animated_tileset_get(
                self.preview_tile.index, 0, self.preview_tile.flip
            )

        elif self.current_tileset == "static":
            self.preview_tile.set(
                {
                    "index": index,
                    "collision": self.preview_tile.collision,
                    "flip": self.preview_tile.flip,
                    "animated":False
                }
            )
            self.preview_tile_img = lib.tileset_get(
                self.preview_tile.index, self.preview_tile.flip
            )
        self.set_tool("brush")

    def set_page(self, page=0):
        tileset = (
            lib.animated_tileset_cache
            if self.current_tileset == "animated"
            else lib.tileset_cache
        )
        # print(page, (len(tileset) - 1) // 8)
        if page <= 0:
            self.page_button_up.disable()
        else:
            self.page_button_up.enable()
        if page == (len(tileset) - 1) // 8:
            self.page_button_down.disable()
        else:
            self.page_button_down.enable()
        if page * 8 >= len(tileset):
            return
        if page < 0:
            return
        self.pages[self.current_tileset] = page
        self.page_num.set_text(str(page + 1))
        self.update_selector()

    def set_layer(self, layer=None):
        if layer == None:
            layer = self.app.level.layers[0][0]
        self.current_layer = layer
        for panel in lib.get_by_id(self.gui_list, "layer_label"):
            if panel.get_text() == self.current_layer:
                panel.set_color(lib.dark_turquoise)
            else:
                panel.set_color(lib.wet_blue)

        if self.show_single:

            for layer in self.app.level.layers:
                if layer[0] == self.current_layer:
                    layer[1].show()
                else:
                    layer[1].hide()
            self.update_layer_selector()

    def add_layer(self, text):
        if text == None:
            return
        if text in self.app.level.get_layer_list():
            return
        self.modify()
        if self.app.level.add_layer(text):
            self.set_layer(text)
        

    def remove_layer(self, layer):
        self.modify()

        res = self.app.level.remove_layer(layer)
        self.set_layer()
        return res

    def swap_layers(self, index1, index2):
        self.modify()

        if not self.app.level.swap_layers(index1, index2):
            return
        self.update_layer_selector()

    def get_selection_tiles(self):
        if not self.sf.visible:
            return None
        pos = self.app.get_virtual_pos(self.sf.rect.topleft)
        tiles = []
        for y in range(0, +self.sf.rect.h // 64):
            for x in range(0, self.sf.rect.w // 64):
                tile = self.app.level.get(pos[0] + x, pos[1] + y, self.current_layer)
                if tile:
                    tiles.append(tile)
        return tiles

    def rename_layer(self, oldname, new_name):
        # print(oldname, new_name)
        if oldname == None or new_name == None:
            return
        self.modify()

        if not self.app.level.rename_layer(oldname, new_name):
            return
        if oldname == self.current_layer:
            self.set_layer(new_name)

    def toggle_single_layer(self):
        self.show_single = not self.show_single
        for layer in self.app.level.layers:
            if layer[0] == self.current_layer or not self.show_single:
                layer[1].show()
            elif self.show_single:
                layer[1].hide()
        self.update_layer_selector()

    def onkeydown(self, key, caps=None):
        self.shift_key = caps
        control = pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_LCTRL]

        if key == K_q:
            self.app.player.go_to(
                [i * 64 + 32 for i in self.app.get_virtual_mouse_pos()], "center"
            )
        elif key == K_e:
            self.app.set_mode("game")
        elif key == K_ESCAPE:
            self.app.set_mode("settings")
        elif key == K_o:
            self.toggle_single_layer()
        elif key == K_s:
            if not control:
                print("Spawn")
                self.set_tool("spawn")
            else:
                print("Save")
                self.save_button.click()
        elif key == K_b:
            self.set_tool("brush")
        elif key == K_m:
            self.set_tool("select")
        elif key == K_c and control:
            print("COPY")
        elif key == K_v and control:
            print("PASTE")
        elif key == K_z and control:
            print("UNDO")
            self.undo_button.click()
        elif self.tool == "select" and key == K_DELETE:
            self.remove_selection()

    def onkeypress(self, keys):
        # print((keys[K_RIGHT]-keys[K_LEFT])*10)
        self.camera_vel.x = (keys[K_RIGHT] - keys[K_LEFT]) * (
            1 if not self.shift_key else 2
        )
        self.camera_vel.y = (keys[K_DOWN] - keys[K_UP]) * (
            1 if not self.shift_key else 2
        )

    def on_enter_mode(self,bool:skip=False):
        # self.inspector_button.hide()
        self.app.player.toggle_control(False)
        self.app.player.update(0)
        self.update_layer_selector()
        self.set_layer(self.current_layer)
        if skip:
            super().on_enter_mode()
            return
        self.on_enter_mode_glide_in()

    def enter_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.fill(lib.dark_turquoise)
        res = self.app.level.blit_layers(hitbox=self.app.show_hitbox)
        self.app.debugger.set("CPH", str(res))

        self.app.player.draw()

        self.glide_in_update(dt, mouse, mouse_button, mouse_pressed)
        self.app.camera.target += self.camera_target

        self.app.camera.update(dt)
    def on_exit_mode(self, exit_event):
        self.app.player.toggle_control(True)

        for layer in self.app.level.layers:
            layer[1].show()
        super().on_exit_mode_glide_out(exit_event)

    def exit_update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.fill(lib.dark_turquoise)
        self.app.level.update(dt)
        res = self.app.level.blit_layers(hitbox=self.app.show_hitbox)
        self.app.debugger.set("CPH", str(res))
        self.app.player.draw()
        return super().glide_out_update(dt, mouse, mouse_button, mouse_pressed)
    def active_update(self, dt, mouse, mouse_button, mouse_pressed):

        self.display.fill(lib.dark_turquoise)
        self.app.level.update(dt)
        res = self.app.level.blit_layers(hitbox=self.app.show_hitbox)
        self.app.debugger.set("CPH", str(res))
        self.app.player.draw()

        if self.main_panel.rect.collidepoint(mouse):
            self.hovered_tile = None
            self.hovered_layer_tile = None
        else:
            # self.hovered_tile = self.app.level.get_first(*self.app.virtual_mouse)
            self.hovered_layer_tile = self.app.level.get(
                *self.app.virtual_mouse, self.current_layer
            )
        
        self.display.blit(
            self.spawn_indicator,
            self.app.level.spawn_point - self.app.camera.int_pos - self.spawn_offset,
        )
        pygame.draw.rect(
            self.display,
            lib.cloud_white,
            (
                *self.app.level.spawn_point
                - self.app.camera.int_pos
                - self.spawn_offset,
                64,
                64,
            ),
            2,
        )
        if self.tool == "brush":
            if not self.main_panel.rect.collidepoint(mouse):
                self.preview_border.topleft = (
                    self.app.virtual_mouse[0] * 64,
                    self.app.virtual_mouse[1] * 64,
                )
                self.preview_border.topleft -= self.app.camera.int_pos
                self.preview_tile.rect.center = mouse

                # draw a preview border where the tile should be
                pygame.draw.rect(
                    self.display,
                    lib.darker_red
                    if any(i < 0 for i in self.app.virtual_mouse)
                    else lib.cloud_white,
                    self.preview_border,
                    3,
                )
                if self.hovered_layer_tile and mouse_pressed[2]:
                    self.modify()
                    self.app.level.remove(*self.app.virtual_mouse, self.current_layer)

                elif mouse_pressed[0] and (
                    not self.hovered_layer_tile
                    or not self.hovered_layer_tile.equals(self.preview_tile)
                ):
                    self.modify()
                    self.app.level.set(
                        *self.app.virtual_mouse,
                        self.current_layer,
                        self.preview_tile.format(),
                    )

                elif mouse_button[2]:
                    self.preview_tile.flip = not self.preview_tile.flip
                    self.select_tile(self.preview_tile.index)

                # draw the tile image (with border) centered at mouse pos
                self.display.blit(self.preview_tile_img, self.preview_tile.rect)
                pygame.draw.rect(
                    self.display, lib.light_blue, self.preview_tile.rect, 3
                )
        elif self.tool == "select":
            if not self.inspector_button.rect.collidepoint(
                mouse
            ) and not self.remove_selection_button.rect.collidepoint(mouse):
                if self.main_panel.rect.collidepoint(mouse):
                    self.sf.update_pos()
                else:
                    self.sf.update(
                        dt,
                        (
                            mouse[0] + self.app.camera.int_pos.x,
                            mouse[1] + self.app.camera.int_pos.y,
                        ),
                        mouse_button,
                        mouse_pressed,
                    )

            if any(x > 0 for x in self.sf.rect.size):
                pygame.draw.rect(
                    self.display,
                    self.sf.border_color,
                    self.sf.rect,
                    self.sf.border,
                    self.sf.border_radius,
                )

            if (
                not self.sf.visible
                or self.main_panel.rect.collidepoint(self.sf.rect.topright)
                or any(x < 64 for x in self.sf.rect.size)
            ):
                self.inspector_button.hide()
                self.remove_selection_button.hide()
            else:
                if self.sf.rect.size == (64, 64):
                    self.inspector_button.show()
                    self.inspector_button.rect.bottomleft = self.sf.rect.move(
                        5, -5
                    ).topright
                    self.remove_selection_button.show()
                    self.remove_selection_button.rect.topright = (
                        self.inspector_button.rect.move(-5, 0).topleft
                    )
                else:
                    self.inspector_button.hide()
                    self.remove_selection_button.rect.bottomleft = self.sf.rect.move(
                        5, -5
                    ).topright
                    self.remove_selection_button.show()

        elif self.tool == "spawn":
            if mouse_button[1] and not self.main_panel.rect.collidepoint(mouse):
                self.modify()
                self.app.level.set_spawn_point(
                    self.app.virtual_mouse[0] * 64 + 32,
                    self.app.virtual_mouse[1] * 64 + 32,
                )

        for panel in self.gui_list:
            panel.update(dt, mouse, mouse_button, mouse_pressed)
            if panel.visible and panel.uid not in ["tile_button"]:
                self.display.blit(panel.image, panel.rect)

        for x, tile_button in enumerate(lib.get_by_id(self.gui_list, "tile_button")):
            if (
                self.selected_tiles[self.current_tileset]
                == x + 8 * self.pages[self.current_tileset]
            ):
                anim_rect = tile_button.rect.move(
                    0, 3 * cos(pygame.time.get_ticks() / 100)
                )
                self.display.blit(tile_button.image, anim_rect)
                pygame.draw.rect(self.display, lib.turquoise, anim_rect, 3)
                continue
            self.display.blit(tile_button.image, tile_button.rect)
            if tile_button.mouse_in:
                pygame.draw.rect(self.display, lib.cloud_white, tile_button.rect, 3)
            else:
                pygame.draw.rect(self.display, lib.darker_blue, tile_button.rect, 3)

        self.app.camera.target += self.camera_vel * dt * self.camera_speed
        self.camera_vel.update(0,0)
        #self.app.camera.target += self.camera_target

        self.app.camera.update(dt)
        self.app.debugger.set(
            "Tile",
            self.hovered_layer_tile.format() if self.hovered_layer_tile else None,
        )
