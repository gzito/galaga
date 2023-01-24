import random

import glm
import pygame as pg
from pyjam.application import Game, pcy2vy
from pyjam.constants import *
from pyjam.sprite import Sprite
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.frame import SpriteFrame
from pyjam.sprites.sheet import SpriteSheet
from pyjam.text import Text, TextAlignment


class JamDrawText(Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)

    def setup_display(self):
        self.set_virtual_display_resolution(800, 600)
        self.set_display_resolution(1024, 768, flags=pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

        pg.display.set_caption('pyjam Texts')

    def initialize(self):
        self.set_assets_root('../assets')

        self.set_bg_color(pg.Color('aquamarine4'))

        font_sp_sheet = SpriteSheet(self)
        font_sp_sheet.load_rects('fonts/retrogaming.png')

        text1 = Text("LEFT JUSTIFIED", font_sp_sheet)
        text1.position = glm.vec2(400, 32)
        text1.size = glm.vec2(16, 16)
        text1.alignment = TextAlignment.LEFT
        text1.set_char_color(random.randrange(0, len(text1.text)), pg.Color('Purple'))
        self.texts.append(text1)

        text2 = Text("CENTERED", font_sp_sheet)
        text2.position = glm.vec2(400, 64)
        text2.size = glm.vec2(16, 16)
        text2.alignment = TextAlignment.CENTER
        text2.set_char_color(random.randrange(0, len(text2.text)), pg.Color('Green'))
        self.texts.append(text2)

        text3 = Text("RIGHT JUSTIFIED", font_sp_sheet)
        text3.position = glm.vec2(400, 96)
        text3.size = glm.vec2(16, 16)
        text3.alignment = TextAlignment.RIGHT
        text3.set_char_color(random.randrange(0, len(text3.text)), pg.Color('Blue'))
        self.texts.append(text3)


if __name__ == '__main__':
    app = JamDrawText()
    app.run()
