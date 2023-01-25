import random
from enum import IntEnum

import glm
import pygame as pg

from pyjam.application import pc2v, GameState
from pyjam.constants import ASSET_SERVICE
from pyjam.sprite import Sprite
from pyjam.sprites.animation import Animation2D

from constants import *

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
        MEM_CHECK = 1,
        RAM_OK = 2,
        SHOW_GRID = 3,
        END_HW_STARTUP = 4

    def __init__(self, game, substate):
        super().__init__(game)
        self.__game = game
        self.__state_timer = 0.0
        self.__substate = substate
        self.__scratch1 = 0
        self.__flipflop = 0
        self.__stage = 0
        self.__xp = 0
        # tiles[ORIGINAL_Y_CELLS][ORIGINAL_X_CELLS], a matrix of Tile
        self.__tiles = [[Tile() for x in range(ORIGINAL_X_CELLS)] for y in range(ORIGINAL_Y_CELLS)]
        self.__memcheck_timer = 0.0
        self.__font_sheet = None

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
                    self.__tiles[y][x].sprite.frame = self.__font_sheet.frames[str(31+character)]

    def mem_check(self):
        if self.__scratch1 == 0:
            self.__font_sheet = self.__game.services[ASSET_SERVICE].get('fonts/font')
            # Make sprites for tiles
            for y in range(ORIGINAL_Y_CELLS):
                for x in range(ORIGINAL_X_CELLS):
                    self.__tiles[y][x].sprite = Sprite(self.__font_sheet.frames['32'])
                    self.__tiles[y][x].char_num = random.randint(1, NUM_CHARS_IN_FONT)
                    self.__tiles[y][x].st = random.randint(1, 5)

                    self.__tiles[y][x].sprite.size = pc2v(glm.vec2(4, 3.0))
                    self.__tiles[y][x].sprite.position = pc2v(glm.vec2(x * (100.0 / ORIGINAL_X_CELLS),
                                                                       y * (100.0 / ORIGINAL_Y_CELLS)))

                    self.__game.sprites.append(self.__tiles[y][x].sprite)

            self.__state_timer = 0.0
            self.__flipflop = 0
            self.__stage = self.__flipflop
            # fill the screen with tiles
            self.update_block(0, 0, ORIGINAL_X_CELLS - 1, ORIGINAL_Y_CELLS - 1)
            self.__memcheck_timer = 0
            self.__scratch1 = 1
        elif self.__scratch1 > 0:
            self.__state_timer += self.__game.delta_time
            if self.__state_timer < 8.0:
                self.__memcheck_timer += self.__game.delta_time
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
                        self.__game.sprites.remove(self.__tiles[y][x].sprite)
                self.substate = HwStartupState.Substate.RAM_OK

        # Tick stages over
        if 2.0 < self.__state_timer <= 4.0:
            self.__stage = 2
        elif 4.0 < self.__state_timer <= 6.0:
            self.__stage = 3
        elif self.__state_timer > 6.0:
            self.__stage = 4

    def ram_ok(self):
        self.substate = HwStartupState.Substate.SHOW_GRID

    def show_grid(self):
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
