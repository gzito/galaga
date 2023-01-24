import os

import pygame as pg

from pyjam.constants import *
from pyjam.sprites.frame import SpriteFrame


class SpriteSheet:
    def __init__(self, game):
        self.__texture_mgr = game.services[TEXTURE_SERVICE]
        self.__cell_width = 0
        self.__cell_height = 0
        self.__num_items = 0
        # Texture2D
        self.__texture2d = None
        # individual sprite frames
        self.frames = {}
        # used only for bitmapped fonts
        self.kerning_width = 0.0
        self.__game = game

    @property
    def texture2d(self):
        return self.__texture2d

    def save_rect_file(self, filename):
        with open(filename, 'w') as f:
            for key, frame in self.frames.items():
                f.write(f'{key}:{frame.rect.x}:{frame.rect.y}:{frame.rect.w}:{frame.rect.h}\n')

    def load_grid(self, filename, frame_name, cw, ch, item_x, item_y, starting_id=0):
        self.__texture2d = self.__texture_mgr.load_texture(filename)
        self.__cell_width = cw
        self.__cell_height = ch
        y = 0
        i = starting_id

        iy = 0
        while iy < item_y:
            x = 0
            ix = 0
            while ix < item_x:
                rectangle = pg.Rect(x, y, cw, ch)
                if frame_name == '':
                    fname = f'{i}'
                else:
                    fname = f'{frame_name}_{i}'
                self.frames[fname] = SpriteFrame(self.__texture2d, rectangle)
                x += cw
                ix += 1
                i += 1
            y += ch
            iy += 1

        self.__num_items = i - starting_id
        self.__game.services[ASSET_SERVICE].insert(filename, self)

    def load_rects(self, filename):
        self.__texture2d = self.__texture_mgr.load_texture(filename)

        i = 0
        asset_root = self.__game.get_assets_root()
        filename_without_ext = os.path.splitext(filename)
        rect_filename = filename_without_ext[0] + '.rects'
        file1 = open(os.path.join(asset_root, rect_filename), 'r')
        for line in file1:
            line = line.strip()
            # skip enmpty lines
            if len(line) == 0:
                continue
            items = line.split(":")
            rectangle = pg.Rect(int(items[1]), int(items[2]), int(items[3]), int(items[4]))
            self.frames[items[0]] = SpriteFrame(self.__texture2d, rectangle)
            i += 1

        self.__num_items = i
        self.__game.services[ASSET_SERVICE].insert(filename, self)
