from enum import Enum

import glm
import pygame as pg

import pyjam.utils
from pyjam.sprites.batch import SpriteBatch, SpriteEffects
from pyjam.sprites.sheet import SpriteSheet


class TextAlignment(Enum):
    LEFT = 0,
    CENTER = 1,
    RIGHT = 2


class Text:
    def __init__(self, text: str, sheet_or_font):
        self.__text = text
        self.__position = glm.vec2(0)
        self.__size = glm.vec2()
        self.__visible = True
        self.__active = True
        self.__layer_depth = 0.1
        self.__sheet_or_font = sheet_or_font
        self.__hotspot = glm.vec2(0)
        self.__scale = glm.vec2(1, 1)
        self.__angle = 0.0
        self.__alignment = TextAlignment.LEFT
        self.__color = pg.Color('White')
        self.__char_colors = []
        self.__use_char_colors = False

    def total_width(self):
        return len(self.__text) * self.__size.x

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value
        if self.__use_char_colors:
            if len(self.__text) > len(self.__char_colors):
                while len(self.__text) > len(self.__char_colors):
                    self.__char_colors.append(pg.Color(self.__color))
            elif len(self.__text) < len(self.__char_colors):
                while len(self.__text) < len(self.__char_colors):
                    self.__char_colors.pop()

    @property
    def position(self) -> glm.vec2:
        return self.__position

    @position.setter
    def position(self, value: glm.vec2):
        self.__position = glm.vec2(value)

    @property
    def size(self) -> glm.vec2:
        return self.__size

    @size.setter
    def size(self, value: glm.vec2):
        self.__size = glm.vec2(value)

    @property
    def color(self) -> pg.Color:
        return self.__color

    @color.setter
    def color(self, value: pg.Color):
        self.__color = value
        self.__char_colors.clear()
        self.__use_char_colors = False

    def get_char_color(self, idx):
        if not self.__use_char_colors:
            return self.__color
        else:
            return self.__char_colors[idx]

    def set_char_color(self, idx, value):
        if not self.__use_char_colors:
            self.__char_colors.clear()
            for i in range(len(self.__text)):
                self.__char_colors.append(pg.Color(self.__color))
            self.__use_char_colors = True

        self.__char_colors[idx] = pg.Color(value)

    @property
    def visible(self) -> bool:
        return self.__visible

    @visible.setter
    def visible(self, flag: bool):
        self.__visible = flag

    @property
    def active(self) -> bool:
        return self.__active

    @active.setter
    def active(self, flag: bool):
        self.__active = flag

    @property
    def angle(self) -> float:
        return self.__angle

    @angle.setter
    def angle(self, value):
        self.__angle = pyjam.utils.wrap_angle_deg_180(value)

    @property
    def layer_depth(self) -> float:
        return self.__layer_depth

    @layer_depth.setter
    def layer_depth(self, value):
        self.__layer_depth = value

    @property
    def hotspot(self) -> glm.vec2:
        return self.__hotspot

    @hotspot.setter
    def hotspot(self, value: glm.vec2):
        self.__hotspot = glm.vec2(value)

    @property
    def scale(self) -> glm.vec2:
        return self.__scale

    @scale.setter
    def scale(self, value: glm.vec2):
        self.__scale = glm.vec2(value)

    @property
    def alignment(self):
        return self.__alignment

    @alignment.setter
    def alignment(self, value):
        self.__alignment = value

    def update(self, delta_time: float):
        pass

    def render(self, batch: SpriteBatch):
        if self.visible:
            if type(self.__sheet_or_font) is SpriteSheet:
                pos = glm.vec2(self.position)
                if self.__alignment == TextAlignment.CENTER:
                    total_width = self.total_width()
                    pos.x -= total_width / 2.0
                elif self.__alignment == TextAlignment.RIGHT:
                    total_width = self.total_width()
                    pos.x -= total_width

                if self.__use_char_colors:
                    colors = self.__char_colors
                else:
                    colors = [self.__color] * len(self.text)

                batch.draw_string(sp_sheet=self.__sheet_or_font,
                                  text=self.text,
                                  position=pos,
                                  w=self.size.x, h=self.size.y,
                                  rotation=self.angle,
                                  chars_colors=colors,
                                  kerning_width=self.__sheet_or_font.kerning_width,
                                  layer_depth=self.layer_depth)
            else:
                if self.size != glm.vec2(0, 0):
                    scale = glm.vec2(self.size.x / self.__sheet_or_font.size, self.size.y / self.__sheet_or_font.size)
                else:
                    scale = self.scale
                batch.draw_string_sprite_font_ex(self.__sheet_or_font, self.text, self.position, self.color,
                                                 self.angle, self.hotspot, scale,
                                                 SpriteEffects.NONE, self.layer_depth)
