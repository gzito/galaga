import glm
import pygame as pg
from pyjam.application import Game
from pyjam.constants import *
from pyjam.sprite import Sprite
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.frame import SpriteFrame


class JamDrawSortMode(Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)

    def setup_display(self):
        self.set_virtual_display_resolution(800, 600)
        self.set_display_resolution(1024, 768, flags=pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

        pg.display.set_caption('pyjam Sprites')

    def initialize(self):
        self.set_assets_root('../assets')

        self.set_bg_color(pg.Color('aquamarine4'))

        asset_service = self.services[ASSET_SERVICE]
        texture_service = self.services[TEXTURE_SERVICE]

        test_frame = texture_service.load_sprite_frame('textures/test.png')

        white_frame = SpriteFrame(texture_service.create_color_texture(pg.Color('white')))

        # red behind
        box1 = Sprite(white_frame)
        box1.size = glm.vec2(64, 64)
        box1.position = glm.vec2(400-33, 300-33)
        box1.color = pg.Color('red')
        box1.layer_depth = 0.9
        self.sprites.append(box1)

        # blue in-front of red
        box2 = Sprite(white_frame)
        box2.size = glm.vec2(64, 64)
        box2.position = glm.vec2(400, 300)
        box2.color = pg.Color('blue')
        box2.layer_depth = 0.2
        self.sprites.append(box2)

        # textured in front of blue
        box3 = Sprite(test_frame)
        box3.size = glm.vec2(64, 64)
        box3.position = glm.vec2(400+33, 300+33)
        box3.layer_depth = 0.1
        self.sprites.append(box3)

        print('box1.collide(box2): ', box1.collide(box2))
        print('box1.collide(box3): ', box1.collide(box3))
        print('box2.collide(box3): ', box2.collide(box3))

    def render(self):
        batch = self.get_sprite_batch()

        batch.begin(sort_mode=SpriteSortMode.BACK_TO_FRONT, transform_matrix=self.get_virtual_matrix())

        for s in self.sprites:
            s.render(batch)

        batch.end()


if __name__ == '__main__':
    app = JamDrawSortMode()
    app.run()
