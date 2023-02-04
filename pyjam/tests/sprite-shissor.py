import glm
import pygame as pg
from Box2D import b2PolygonShape

from pyjam.application import Game
from pyjam.constants import *
from pyjam.sprite import Sprite
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.frame import SpriteFrame


class JamSpriteScissor(Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)

        self.step = 0.5
        self.speed = 30.0
        self.blue_box = None
        self.red_box = None
        self.yellow_box = None
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
        self.set_sprite_batch_sort_mode(SpriteSortMode.BACK_TO_FRONT)
        # self.set_sprite_batch_sort_mode(SpriteSortMode.FRONT_TO_BACK)

        texture_service = self.services[TEXTURE_SERVICE]

        test_frame = texture_service.load_sprite_frame('textures/test.png')
        white_frame = SpriteFrame(texture_service.create_color_texture(pg.Color('white')))

        # blue
        self.blue_box = box1 = Sprite(white_frame)
        box1.size = glm.vec2(64, 64)
        box1.position = glm.vec2(300, 200)
        box1.color = pg.Color('blue')
        box1.layer_depth = 0.9
        self.sprites.append(box1)

        # red
        self.red_box = box2 = Sprite(white_frame)
        box2.size = glm.vec2(64, 64)
        box2.position = glm.vec2(400, 200)
        box2.color = pg.Color('red')
        box2.layer_depth = 0.8
        self.sprites.append(box2)

        # yellow
        self.yellow_box = box3 = Sprite(white_frame)
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
        if self.key_down(pg.K_LEFT):
            self.yellow_box.x -= self.speed * self.delta_time
        elif self.key_down(pg.K_RIGHT):
            self.yellow_box.x += self.speed * self.delta_time

        if self.key_down(pg.K_UP):
            self.yellow_box.y -= self.speed * self.delta_time
        elif self.key_down(pg.K_DOWN):
            self.yellow_box.y += self.speed * self.delta_time

        if self.textured_box.scissor is None:
            self.textured_box.scissor = self.textured_box.bounds
            self.textured_box.scissor.h = 1

        self.textured_box.scissor.h += self.step

        center_x = 0
        center_y = (self.textured_box.scissor.h-self.textured_box.bounds.h) / 2
        self.textured_box.shape = b2PolygonShape(
            box=(self.textured_box.size.x / 2.0, self.textured_box.scissor.h / 2.0, (center_x, center_y), 0.0))

        if self.textured_box.scissor.h >= self.textured_box.bounds.h:
            self.textured_box.scissor.h = self.textured_box.bounds.h
            self.step = -self.step
        elif self.textured_box.scissor.h < 0.0:
            self.textured_box.scissor.h = 1
            self.step = -self.step

        if self.yellow_box.collide(self.textured_box):
            self.yellow_box.color = pg.Color('green')
        else:
            self.yellow_box.color = pg.Color('yellow')


if __name__ == '__main__':
    app = JamSpriteScissor()
    app.run()
