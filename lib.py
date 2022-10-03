import pygame
import json
import os
from pandas import read_csv as pd_read_csv
from pandas import isnull as pd_isnull
import re


df = pd_read_csv("script/dialogues.csv", sep="|", header=[0])

lang = "en"
langs = list(df)[1:]
default_text_size = 18
small_font = 12
big_font = 24
from pygame.locals import SRCALPHA

pygame.font.init()

fonts = {}

for size in [12, 18, 24, 36, 48, 60, 72]:
    fonts[size] = pygame.font.Font("fonts/mochiy.ttf", size)
fonts["title"] = pygame.font.Font("fonts/verdana.ttf", 100, italic=True)


def blend_color(color1, color2):
    for i, value in enumerate(color1):
        color2[i] = min((value + color2[i]) // 2, 255)
    return color2


FPS = 120
GRAVITY = 2700
FRICTION = 0.7
WIDTH = 1280  # 1024
HEIGHT = 720  # 768
DISPLAY_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)

INPUTBOX = pygame.event.custom_type()
DIALOG = pygame.event.custom_type()
SET_MODE = pygame.event.custom_type()

level_path = "levels/"
tileset_path = "Assets/Tiles/tileset.png"
animated_tileset_path = "Assets/Tiles/animated_tileset.png"

dark_blue = [44, 62, 80]
wet_blue = [52, 73, 94]
light_blue = blend_color(wet_blue, [255, 255, 255])
river_blue = [52, 152, 219]
dark_red = [192, 57, 43]
dark_green = [39, 174, 96]
sky_blue = [52, 152, 219]
silver = [189, 195, 199]
dark_gray = [127, 140, 141]
darker_gray = blend_color(dark_gray, [20, 20, 20])
cloud_white = [236, 240, 241]
turquoise = [26, 188, 156]
dark_turquoise = blend_color([22, 160, 133], [30, 30, 30])
darker_turquoise = blend_color(dark_turquoise, [30, 30, 30])
transparent = [0, 0, 0, 0]
darker_red = blend_color(dark_red, [40, 40, 40])
darker_blue = blend_color(dark_blue, [10, 10, 10])
darker_green = blend_color(dark_green, [10, 10, 10])


animated_tile_duration = {0: [15, 60, 15, 60], 1: [10] * 7, 4: [10] * 10, 3: [20] * 4}

interactive_tiles = [8, 9, 27, 28, 23, 22, 14]

character_sprites = {}

tileset_cache = {}
animated_tileset_cache = []


def set_lang(language):
    global lang
    if language not in langs:
        return
    lang = language


def get_dialog_data(uid):
    df = pd_read_csv("script/dialogues.csv", sep="|", header=[0])
    data = (df.loc[df["ID"] == uid, lang]).tolist()
    if pd_isnull(data):
        print("Error : No such data : ", uid)
        return []
    # print(data)
    return data[0]


def post_dialog(act, dat):
    pygame.event.post(pygame.event.Event(DIALOG, action=act, data=dat))


def post_dialogs_by_id(uid):
    data = get_dialog_data(uid)
    master_commands= []
    if not data:
        return
    for message in data.split("§"):
        #print(message)
        master_commands = re.findall("\(mc *,[^\)]+\)",message)
        message = re.sub("\(mc *,[^\)]+\)",'',message)
        post_dialog("SAY", {"text": message,"master_commands":master_commands})


def get_by_id(gui_list, uid):

    if uid == "":
        return gui_list
    res = []
    for panel in gui_list:
        if panel.uid == uid:
            res.append(panel)
    return res


def load_data(path):
    if not os.path.exists(path):
        return False
    with open(path, "r") as f:
        data = json.load(f)
    return data


def save_data(path, data):
    with open(path, "w+") as f:
        json.dump(data, f)


def remove_file(path):
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        return False
    os.remove(path)
    return True


def change_size(width, height):
    global WIDTH
    global HEIGHT
    if width:
        WIDTH = width
    if height:
        HEIGHT = height


def remove_color(surf, color):
    surf.set_colorkey(color)
    surf.convert_alpha()
    return surf


def tile_to_pixel(tile_data):
    if not tile_data:
        return (0, 0, 0, 0)
    # print(tile_data)
    index = tile_data["index"]
    img = (
        animated_tileset_get(index)
        if "animation_counter" in tile_data
        else tileset_get(index)
    )
    return pygame.transform.average_color(img, (0, 0, 64, 64))


def level_to_pixel(level_data):
    chunk_size = level_data["chunk_size"]
    size = level_data["size"] * chunk_size
    surf = pygame.surface.Surface((size, size), pygame.SRCALPHA)
    for layer in reversed(level_data["layers"]):
        if not layer[1]:
            continue
        for y, row in enumerate(layer[1]):
            for x, chunk in enumerate(row):
                if not chunk:
                    continue
                for pos, tile in chunk.items():
                    tile_pos = [int(i) for i in pos.split(",")]
                    tile_x = tile_pos[0] + (chunk_size * x)
                    tile_y = tile_pos[1] + (chunk_size * y)
                    if surf.get_at((tile_x, tile_y)) != (0, 0, 0, 0):
                        continue
                    surf.set_at((tile_x, tile_y), tile_to_pixel(tile))

    return surf


def load_image(path, scale):
    surf = pygame.image.load(path).convert_alpha()
    surf = pygame.transform.scale(surf, scale)
    return surf


def animated_tileset_get(index, frame, flip=False):
    global animated_tileset_cache
    if flip and not animated_tileset_cache[index][frame][True]:
        animated_tileset_cache[index][frame][True] = pygame.transform.flip(
            animated_tileset_cache[index][frame][False], True, False
        )
    return animated_tileset_cache[index][frame][flip]


def tileset_get(index, flip=False):
    global tileset_cache
    if flip and not tileset_cache[index][True]:
        tileset_cache[index][True] = pygame.transform.flip(
            tileset_cache[index][False], True, False
        )
    return tileset_cache[index][flip]


def load_tileset(path=tileset_path, scale=(64, 64)):
    global tileset_cache
    tileset_cache = {}
    img = pygame.image.load(path).convert_alpha()
    width = img.get_width() // 16
    height = img.get_height() // 16
    sheet = []
    for y in range(height):
        for x in range(width):
            sheet.append(img.subsurface([x * 16, y * 16, 16, 16]))
    for i, surf in enumerate(sheet):
        surf = pygame.transform.scale(surf, scale)
        sheet[i] = surf.copy()
        tileset_cache[i] = {}
        tileset_cache[i][False] = surf.copy()
        tileset_cache[i][True] = None

    return sheet


# [ [frame1,frame2,frame3], [frame1,frame2] ]
def load_animated_tileset(path=animated_tileset_path, scale=(64, 64)):
    global animated_tileset_cache
    animated_tileset_cache = []
    img = pygame.image.load(path).convert_alpha()
    # img.convert_alpha()
    img.set_colorkey((0, 0, 0, 0))
    width = img.get_width() // 16
    height = img.get_height() // 16
    scaled_surf = pygame.surface.Surface(scale, SRCALPHA)
    # scaled_surf.fill((0,0,0,0))
    sheet = []
    for y in range(height):
        sheet.append([])
        animated_tileset_cache.append([])

        for x in range(width):
            if img.get_at((x * 16, y * 16)) == (0, 0, 0, 255):
                break
            pygame.transform.scale(
                img.subsurface([x * 16, y * 16, 16, 16]), scale, scaled_surf
            )
            sheet[y].append(scaled_surf.copy())
            animated_tileset_cache[y].append({})
            animated_tileset_cache[y][x][False] = scaled_surf.copy()
            animated_tileset_cache[y][x][True] = None

    return sheet


def get_text_size(text, font_size):
    if font_size in fonts.keys():
        font = fonts[font_size]
    else:
        font = list(fonts.values())[0]
    return font.size(text)


def render_text(text, font_size=0, color=(255, 255, 255)):

    if font_size in fonts.keys():
        font = fonts[font_size]
    else:
        font = list(fonts.values())[0]
    size = font.size(text)
    surf = pygame.surface.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    if font == fonts["title"]:
        string_render = font.render(text, 1, color)

    else:
        string_render = font.render(text, 1, color)
    surf.blit(string_render, (0, 0))
    return surf


def get_files_in_dir(path, ext=None):
    files = []
    if not os.path.isdir(path):
        return []
    for filename in os.listdir(path):
        full_name = os.path.join(path, filename)
        if os.path.isfile(full_name):
            if ext and not full_name.endswith(ext):
                continue
            files.append(full_name)
    return files


def load_character_sprites():
    global character_sprites
    if not character_sprites == {}:
        return character_sprites
    path_to_character_animation = "Assets/characters/"

    for filename in os.listdir(path_to_character_animation):
        dir = os.path.join(path_to_character_animation, filename)
        if not os.path.isdir(dir):
            continue
        character_sprites[filename] = {}
        for image_file in os.listdir(dir):
            image_path = os.path.join(dir, image_file)
            if not os.path.isfile(image_path):
                continue
            if not image_file.split(".")[1] == "png":
                continue
            character_sprites[filename][image_file.split(".")[0]] = load_image(
                image_path, (640, 720)
            )
    return character_sprites
