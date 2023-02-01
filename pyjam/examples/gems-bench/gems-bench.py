import random

import glm
import pygame as pg

from pyjam.constants import *
from pyjam import application, utils
from pyjam.sprites.animation import Animation2D
from pyjam.sprites.batch import SpriteSortMode
from pyjam.sprites.sheet import SpriteSheet
from pyjam.sprites.font import SpriteFont
from pyjam.text import Text
from pyjam.sprite import Sprite


class JamSprites(application.Game):
    def __init__(self):
        super().__init__()

        self.set_framerate(60)
        self.set_assets_root('../../assets')

        self.animations = {}
        self.gem_types = ['yellow', 'ice', 'blue', 'red', 'purple', 'orange', 'green']

    def setup_display(self):
        self.set_virtual_display_resolution(800, 600)
        self.set_display_resolution(1024, 768, flags=pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL)

        pg.display.set_caption('pyjam Sprites')

    def initialize(self):
        sp_font = SpriteFont(self)
        sp_font.load('fonts/kf-xml.fnt')

        sp_gems_sheet = SpriteSheet(self)
        sp_gems_sheet.load_grid('textures/gemsheet.png', 'gem', 52, 52, 15, 14)

        self.create_animations()

        self.set_bg_color(pg.Color('aquamarine4'))

        self.change_state(JamSpritesState(self))

    def create_animations(self):
        i = 0
        for gem in self.gem_types:
            if gem == 'blue':
                self.create_animation(gem, i, 29)
            else:
                self.create_animation(gem, i, 30)
            i += 30

    def create_animation(self, name, start, count):
        anim = Animation2D(loop=True)
        sp_sheet = self.services[ASSET_SERVICE].get('textures/gemsheet')
        for n in range(start, start + count):
            anim.add_frame(sp_sheet.frames[f'gem_{n}'])
        self.animations[name] = anim


class Gem(Sprite):
    def __init__(self, frame, game):
        super().__init__(frame)
        self.destination = None
        self.timer = 0
        self.game = game
        self.speed = 15.0

    def update(self, delta_time: float):
        if self.timer == 0:
            if self.destination is None:
                self.destination = glm.vec2(random.randint(0, self.game.get_virtual_display_width()),
                                            random.randint(0, self.game.get_virtual_display_height()))
                self.speed = random.randint(15, 60)
            else:
                self.position = utils.vec2_move_torwards(self.position, self.destination, self.speed * delta_time)
                if glm.distance(self.destination, self.position) < 0.0001:
                    self.timer = 2
                    self.destination = None
        else:
            self.timer -= delta_time
            if self.timer < 0:
                self.timer = 0

        super().update(delta_time)


class JamSpritesState(application.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.sprites_counts = 30
        self.sort_mode_idx = SpriteSortMode.DEFERRED

        self.text_fps = self.create_text('fps', glm.vec2(0, 0), glm.vec2(0, 0))
        self.text_sprites_count = self.create_text('sprite-count',
                                                   glm.vec2(0, self.game.get_virtual_display_height() - 64),
                                                   glm.vec2(24, 24))
        self.text_draw_mode = self.create_text('draw-mode',
                                               glm.vec2(0, self.game.get_virtual_display_height() - 32),
                                               glm.vec2(24, 24))
        self.text_help = self.create_text('H Hide/Show help\nS Change Sort mode\n+/- Add / remove sprites',
                                          glm.vec2(0, 64),
                                          glm.vec2(24, 24))

        for i in range(self.sprites_counts):
            self.create_sprite()

    def create_sprite(self):
        x = random.randint(0, self.game.get_virtual_display_width())
        y = random.randint(16, self.game.get_virtual_display_height() - 48)
        frame_num = random.randrange(1, 15 * 14)
        sp_sheet = self.game.services[ASSET_SERVICE].get('textures/gemsheet')
        sprite = Gem(sp_sheet.frames[f'gem_{frame_num}'], self.game)
        sprite.position = glm.vec2(x, y)
        sprite.size = glm.vec2(64, 64)
        anim_name = random.choice(self.game.gem_types)
        sprite.set_animation(self.game.animations[anim_name])
        sprite.play()
        self.game.sprites.append(sprite)
        return sprite

    def create_text(self, text, pos, size):
        asset_font = self.game.services[ASSET_SERVICE].get('fonts/kf-xml')
        text_obj = Text(text, asset_font)
        text_obj.position = pos
        text_obj.size = size
        self.game.sprites.append(text_obj)
        return text_obj

    def handle_input(self):
        if self.game.key_down(pg.K_PLUS):
            self.create_sprite()
        elif self.game.key_down(pg.K_MINUS) and len(self.game.sprites) > 4:
            self.game.sprites.pop()
        elif self.game.key_pressed(pg.K_s):
            self.sort_mode_idx = utils.wrap(self.sort_mode_idx + 1, 0, len(SpriteSortMode) - 1)
            self.game.set_sprite_batch_sort_mode(SpriteSortMode(self.sort_mode_idx))
        elif self.game.key_pressed(pg.K_h):
            self.text_help.visible = not self.text_help.visible
        elif self.game.key_pressed(pg.K_ESCAPE):
            self.game.signal_quit()

    def update(self):
        for s in self.game.sprites:
            s.update(self.game.delta_time)

        fps = self.game.clock.get_fps()
        self.text_fps.text = f'{fps:.0f}'
        if fps >= 30:
            self.text_fps.color = pg.Color('white')
        else:
            self.text_fps.color = pg.Color('red')

        self.text_sprites_count.text = f'Sprites: {len(self.game.sprites) - 4}'
        self.text_draw_mode.text = f'Sort mode: {self.game.get_sprite_batch_sort_mode().name}'


if __name__ == '__main__':
    sprites = JamSprites()
    sprites.run()
