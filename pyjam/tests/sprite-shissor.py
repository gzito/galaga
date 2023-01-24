import glm
import pygame as pg
from pyjam.application import Game
from pyjam.constants import *
from pyjam.sprite import Sprite
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.frame import SpriteFrame


class JamSpriteScissor(Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)

        self.textured_box = None

    def setup_display(self):
        self.set_virtual_display_resolution(800, 600)
        self.set_display_resolution(1024, 768, flags=pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

        pg.display.set_caption('pyjam Sprites')

    def initialize(self):
        self.set_assets_root('../assets')

        self.set_bg_color(pg.Color('aquamarine4'))

        # self.set_sprite_batch_sort_mode(SpriteSortMode.IMMEDIATE)
        # self.set_sprite_batch_sort_mode(SpriteSortMode.TEXTURE)
        # self.set_sprite_batch_sort_mode(SpriteSortMode.DEFERRED)
        # self.set_sprite_batch_sort_mode(SpriteSortMode.BACK_TO_FRONT)
        self.set_sprite_batch_sort_mode(SpriteSortMode.FRONT_TO_BACK)

        texture_service = self.services[TEXTURE_SERVICE]

        test_frame = texture_service.load_sprite_frame('textures/test.png')
        white_frame = SpriteFrame(texture_service.create_color_texture(pg.Color('white')))

        # blue
        box1 = Sprite(white_frame)
        box1.size = glm.vec2(64, 64)
        box1.position = glm.vec2(300, 200)
        box1.color = pg.Color('blue')
        box1.layer_depth = 0.9
        self.sprites.append(box1)

        # red
        box2 = Sprite(white_frame)
        box2.size = glm.vec2(64, 64)
        box2.position = glm.vec2(400, 200)
        box2.color = pg.Color('red')
        box2.layer_depth = 0.8
        self.sprites.append(box2)

        # yellow
        box3 = Sprite(white_frame)
        box3.size = glm.vec2(64, 64)
        box3.position = glm.vec2(300, 300)
        box3.color = pg.Color('yellow')
        box3.layer_depth = 0.8
        self.sprites.append(box3)

        # textured
        self.textured_box = box4 = Sprite(test_frame)
        box4.size = glm.vec2(64, 64)
        box4.position = glm.vec2(400, 300)
        # box1.scale = glm.vec2(2, 2)
        box4.layer_depth = 0.5
        self.sprites.append(box4)

    def update(self):
        if self.textured_box.scissor is None:
            self.textured_box.scissor = self.textured_box.bounds
            self.textured_box.scissor.h = 1
        self.textured_box.scissor.h += 0.5
        if self.textured_box.scissor.h >= self.textured_box.bounds.h:
            self.textured_box.scissor.h = self.textured_box.bounds.h


if __name__ == '__main__':
    app = JamSpriteScissor()
    app.run()
