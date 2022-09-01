from .mode import Mode
import gui as gui
import lib as lib
import pygame
import os


class Inspector(Mode):
    def __init__(self, app, display) -> None:
        self.tile = None
        self.display = display
        self.app = app
        self.gui_list = []
        self.animation_counter = 0
        self.tile_img = None

    def init_gui(self):
        self.gui_list = []
        inspector_panel = gui.Panel(
            self.gui_list,
            0, 0,
            400,lib.HEIGHT,
            color=lib.dark_blue,border_radius=10,
            border=3,border_color=lib.wet_blue
        )
        label =gui.TextBox(
            self.gui_list,
            inspector_panel.rect.x+20,inspector_panel.rect.y+10,
            inspector_panel.rect.w-40,
            30,
            text="inspector",
            color=lib.wet_blue,
            border_radius=10
        )
        gui.Button(
            self.gui_list,
            *label.rect.topleft,
            30,
            30,
            "<",
            func=lambda: self.app.set_mode(self.app.previous_mode),
            color=lib.wet_blue,
            border_radius=10
        )
        self.tile_panel = gui.Panel(
            self.gui_list,
            20,label.rect.bottom+20,
            74,74,
            color=lib.darker_blue,border=3,border_color=lib.wet_blue,

        )
        if not self.tile : return

    def select_tile(self,tile):
        self.tile = tile
        if not tile:
            print("Error : None type tile")
            return
        if tile.animated: 
            self.tile_img = lib.animated_tileset_get(tile.index,0,tile.flip) 
        else:
            self.tile_img = lib.tileset_get(tile.index,tile.flip)
        self.init_gui()
    def update(self, dt, mouse, mouse_button, mouse_pressed):
        self.display.fill(lib.dark_turquoise)

        self.app.level.update(dt)
        self.app.level.blit_layers(hitbox=self.app.show_hitbox)
        self.app.player.draw()
        super().update(dt, mouse, mouse_button, mouse_pressed)
        if self.tile:
            if self.tile.animated : 
                self.animation_counter += 60 * dt
                index = self.tile.get_animation_frame(int(self.animation_counter))
                self.tile_img = lib.animated_tileset_get(
                    self.tile.index,index,self.tile.flip
                )
            self.display.blit(self.tile_img,self.tile_panel.rect.move(5,5))