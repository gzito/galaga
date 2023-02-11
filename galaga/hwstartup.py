import random

import glm
import numpy as np

from pyjam.sprites.batch import SpriteBatch
from pyjam.application import pc2v, GameState, pcy2vy, pcx2vx
from pyjam.constants import ASSET_SERVICE
from pyjam.sprite import Sprite

from galaga_data import *
from pyjam.sprites import primitives2d

NUM_CHARS_IN_FONT = 80
FONT_HEIGHT = 34
FONT_WIDTH = 32


class Tile:
    def __init__(self):
        self.sprite = None
        self.char_num = 0
        self.st = 0


class HwStartupState(GameState):
    class Substate(IntEnum):
        MEM_CHECK = 1
        RAM_OK = 2
        SHOW_GRID = 3
        END_HW_STARTUP = 4

    def __init__(self, game, substate=None):
        super().__init__(game)
        self.__game = game
        self.__state_timer = 0.0
        if substate is None:
            self.__substate = HwStartupState.Substate.MEM_CHECK
        else:
            self.__substate = substate
        self.__scratch1 = 0
        self.__font_sheet = None

        # mem_check variables
        self.__flipflop = 0
        self.__stage = 0
        self.__xp = 0
        # tiles[ORIGINAL_Y_CELLS][ORIGINAL_X_CELLS], a matrix of Tile objects
        self.__tiles = [[Tile() for x in range(ORIGINAL_X_CELLS)] for y in range(ORIGINAL_Y_CELLS)]
        self.__memcheck_timer = 0.0

        # ram_ok variables
        self.pos = [(80, 90), (80, 85), (80, 80), (80, 75), (80, 70), (80, 65), (80, 60), (90, 50), (90, 45), (90, 40)]

        # show_grid variables
        self.sp_batch = None

    @property
    def substate(self):
        return self.__substate

    @substate.setter
    def substate(self, new_state):
        self.__substate = new_state
        self.__scratch1 = 0
        self.__state_timer = 0.0

    def update(self):
        self.startup_sequence()

    def update_block(self, x0, y0, x1, y1):
        character = 1
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                # and 1 alternate with 0 = totally random
                if self.__stage == 0:
                    character = random.randint(1, NUM_CHARS_IN_FONT)
                # 1 shows a set character
                elif self.__stage == 1:
                    character = self.__tiles[y][x].char_num
                # random characters but mostly white squares
                elif self.__stage == 2:
                    if random.randint(1, 5) == 5:
                        character = random.randint(1, NUM_CHARS_IN_FONT)
                    else:
                        character = 80
                # mostly white squares with some random characters and changes along a diagonal
                elif self.__stage == 3:
                    if x + random.randint(-3, 3) == y and random.randint(1, 5) == 5:
                        character = random.randint(1, NUM_CHARS_IN_FONT)
                    else:
                        character = -1
                # mostly white squares with some blocks changing between characters and colors
                elif self.__stage == 4:
                    if self.__tiles[y][x].st == 5:
                        character = random.randint(1, NUM_CHARS_IN_FONT)
                    else:
                        character = 80

                if self.__stage < 2:
                    if character >= 62:
                        self.__tiles[y][x].sprite.color = pg.Color(190, 190, 190, 255)
                    else:
                        self.__tiles[y][x].sprite.color = pg.Color(0, 224, 196, 255)
                else:
                    if character != -1:
                        if character == 80:
                            self.__tiles[y][x].sprite.color = pg.Color(190, 190, 190, 255)
                        else:
                            self.__tiles[y][x].sprite.color = pg.Color(random.randint(50, 255),
                                                                       random.randint(50, 255),
                                                                       random.randint(50, 255),
                                                                       255)

                # if the character is -1 then leave the block unchanged (stage 3)
                if character != -1:
                    self.__tiles[y][x].sprite.frame = self.__font_sheet.frames[str(31 + character)]

    def mem_check(self):
        if self.__scratch1 == 0:
            self.__font_sheet = self.game.services[ASSET_SERVICE].get('fonts/font')
            # Make sprites for tiles
            for y in range(ORIGINAL_Y_CELLS):
                for x in range(ORIGINAL_X_CELLS):
                    self.__tiles[y][x].sprite = Sprite(self.__font_sheet.frames['32'])
                    self.__tiles[y][x].char_num = random.randint(1, NUM_CHARS_IN_FONT)
                    self.__tiles[y][x].st = random.randint(1, 5)

                    self.__tiles[y][x].sprite.size = pc2v(glm.vec2(4, 3.0))
                    self.__tiles[y][x].sprite.position = pc2v(glm.vec2(x * (100.0 / ORIGINAL_X_CELLS),
                                                                       y * (100.0 / ORIGINAL_Y_CELLS)))
                    self.__tiles[y][x].sprite.hotspot = glm.vec2(0, 0)

                    self.game.sprites.append(self.__tiles[y][x].sprite)

            self.__state_timer = 0.0
            self.__flipflop = 0
            self.__stage = self.__flipflop
            # fill the screen with tiles
            self.update_block(0, 0, ORIGINAL_X_CELLS - 1, ORIGINAL_Y_CELLS - 1)
            self.__memcheck_timer = 0
            self.__scratch1 = 1
        elif self.__scratch1 > 0:
            self.__state_timer += self.game.delta_time
            if self.__state_timer < 9.0:
                self.__memcheck_timer += self.game.delta_time
                # wait 50 ms
                if self.__memcheck_timer < 0.05:
                    return
                else:
                    self.__memcheck_timer = 0
                # 1 & 2 have green and white random-ish stuff that moves in blocks
                if self.__stage < 2:
                    if self.__scratch1 == 1:
                        self.__xp = random.randint(ORIGINAL_X_CELLS // 3, ORIGINAL_X_CELLS - 3)
                        self.update_block(self.__xp, 2, ORIGINAL_X_CELLS - 1, ORIGINAL_Y_CELLS - 1)
                        self.update_block(0, ORIGINAL_Y_CELLS - 3, ORIGINAL_X_CELLS - 1, ORIGINAL_Y_CELLS - 1)
                        self.__scratch1 = 2
                    elif self.__scratch1 == 2:
                        self.update_block(0, 2, self.__xp - 1, ORIGINAL_Y_CELLS - 3)
                        self.update_block(0, 0, ORIGINAL_X_CELLS - 1, 1)
                        self.__flipflop = 1 - self.__flipflop
                        self.__stage = self.__flipflop
                        self.__scratch1 = 1
                else:
                    self.update_block(0, 0, ORIGINAL_X_CELLS - 1, ORIGINAL_Y_CELLS - 1)
            else:
                # Delete tile sprites
                for y in range(0, ORIGINAL_Y_CELLS):
                    for x in range(0, ORIGINAL_X_CELLS):
                        self.game.sprites.remove(self.__tiles[y][x].sprite)
                self.substate = HwStartupState.Substate.RAM_OK

        # Tick stages over
        if 3.0 < self.__state_timer <= 5.0:
            self.__stage = 2
        elif 5.0 < self.__state_timer <= 7.0:
            self.__stage = 3
        elif self.__state_timer > 7.0:
            self.__stage = 4

    def ram_ok(self):
        # Show RAM OK
        if self.__scratch1 == 0:
            self.__state_timer = 0.0
            self.game.texts[TEXT_RAM_OK].position = pc2v(glm.vec2(40, 10))
            self.game.texts[TEXT_RAM_OK].visible = True
            self.__scratch1 += 1
        elif self.__scratch1 == 1:
            self.__state_timer += self.game.delta_time
            if self.__state_timer >= 250 / 1000.0:
                self.game.texts[TEXT_RAM_OK].visible = False
                self.__scratch1 += 1
        # Show the status upside-down
        elif self.__scratch1 == 2:
            for i, p in enumerate(self.pos):
                point_index = i + TEXT_RAM_OK
                self.game.texts[point_index].position = pc2v(glm.vec2(self.pos[i]))
                self.game.texts[point_index].angle = 180
                self.game.texts[point_index].visible = True
            self.game.texts[TEXT_SOUND_00].visible = False
            self.__state_timer = 0.0
            self.__scratch1 += 1
        # Hide sound
        elif self.__scratch1 == 3:
            self.__state_timer += self.game.delta_time
            if self.__state_timer >= 250 / 1000.0:
                self.game.texts[TEXT_SOUND_00].visible = True
                self.__state_timer = 0.0
                self.__scratch1 += 1
        # Show sound
        elif self.__scratch1 == 4:
            self.__state_timer += self.game.delta_time
            if self.__state_timer >= 250 / 1000.0:
                self.game.set_text_range_visible(TEXT_RAM_OK, TEXT_EVERY_BONUS, False)
                self.substate = HwStartupState.Substate.SHOW_GRID

    def show_grid(self):
        if self.__scratch1 == 0:
            self.sp_batch = SpriteBatch(self.game)
            self.__scratch1 += 1
            self.game.sfx_play(SOUND_PLAYER_DIE)
            self.__state_timer = 0.0
        elif self.__scratch1 == 1:
            vw = self.game.get_virtual_display_width()
            vh = self.game.get_virtual_display_height()
            dw = self.game.get_display_width()
            dh = self.game.get_display_height()
            sw = float(vw) / dw
            sh = float(vh) / dh

            self.sp_batch.begin(transform_matrix=self.game.get_virtual_matrix())
            texture = self.game.services[ASSET_SERVICE].get('textures/star').texture

            for y in range(ORIGINAL_Y_CELLS // 2 + 1):
                p0 = y * (99.6 / (ORIGINAL_Y_CELLSF / 2))
                p1 = p0 + 0.4
                for y1 in np.arange(p0, p1 + sh, sh):
                    primitives2d.draw_line(self.sp_batch, 0.0, pcy2vy(y1), pcx2vx(100.0), pcy2vy(y1), texture, 1)

            for x in range(ORIGINAL_X_CELLS // 2 + 1):
                p0 = x * (99.6 / (ORIGINAL_X_CELLSF / 2))
                p1 = p0 + 0.4
                for x1 in np.arange(p0, p1 + sw, sw):
                    primitives2d.draw_line(self.sp_batch, pcx2vx(x1), 0.0, pcx2vx(x1), pcy2vy(100.0), texture, 1)
            self.sp_batch.end()

            self.__state_timer += self.game.delta_time
            if self.__state_timer > 0.75:
                self.sp_batch.dispose()
                self.substate = HwStartupState.Substate.END_HW_STARTUP

    def startup_sequence(self):
        if self.substate == HwStartupState.Substate.MEM_CHECK:
            # Flash memory check sequence
            self.mem_check()
        elif self.substate == HwStartupState.Substate.RAM_OK:
            # RAM OK text sequence
            self.ram_ok()
        elif self.substate == HwStartupState.Substate.SHOW_GRID:
            # Grid sequence
            self.show_grid()
