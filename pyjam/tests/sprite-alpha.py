import glm
import pygame as pg

from pyjam import utils
from pyjam.application import Game
from pyjam.constants import *
from pyjam.sprite import Sprite
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.frame import SpriteFrame
from pyjam.sprites.sheet import SpriteSheet
from pyjam.text import Text


class JamSpriteAlpha(Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)

        self.textured_box = None
        self.alpha = 255

    def setup_display(self):
        self.set_virtual_display_resolution(800, 600)
        self.set_display_resolution(1024, 768, flags=pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

        pg.display.set_caption('pyjam Sprites')

    def initialize(self):
        self.set_assets_root('../assets')

        self.set_bg_color(pg.Color('aquamarine4'))

        self.set_sprite_batch_sort_mode(SpriteSortMode.BACK_TO_FRONT)

        texture_service = self.services[TEXTURE_SERVICE]

        test_frame = texture_service.load_sprite_frame('textures/test.png')
        white_frame = SpriteFrame(texture_service.create_color_texture(pg.Color('white')))

        # blue
        box1 = Sprite(white_frame)
        box1.size = glm.vec2(64, 64)
        box1.position = glm.vec2(400-32, 300-32)
        box1.color = pg.Color('blue')
        box1.layer_depth = 0.9
        self.sprites.append(box1)

        # textured
        self.textured_box = box2 = Sprite(test_frame)
        box2.size = glm.vec2(64, 64)
        box2.position = glm.vec2(400, 300)
        box2.layer_depth = 0.5
        self.sprites.append(box2)

        font_sp_sheet = SpriteSheet(self)
        font_sp_sheet.load_rects('fonts/retrogaming.png')
        text1 = Text("PRESS UP/DOWN KEYS TO CHANGE TRANSPARENCY", font_sp_sheet)
        text1.size = glm.vec2(16, 16)
        self.texts.append(text1)

    def update(self):
        if self.key_down(pg.K_UP):
            self.alpha = utils.clamp(self.alpha + 1, 0, 255)
        elif self.key_down(pg.K_DOWN):
            self.alpha = utils.clamp(self.alpha - 1, 0, 255)

        self.textured_box.color = pg.Color(255, 255, 255, self.alpha)


if __name__ == '__main__':
    app = JamSpriteAlpha()
    app.run()
