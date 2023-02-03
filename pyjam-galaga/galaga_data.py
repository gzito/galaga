import os.path

import pygame as pg
from enum import IntEnum
from constants import *
from pyjam.text import TextAlignment


class EntityType(IntEnum):
    FIGHTER = 0,
    CAPTURED_FIGHTER = 1,
    BOSS_GREEN = 2,
    BOSS_BLUE = 3,
    BUTTERFLY = 4,
    BEE = 5,
    SCORPION = 6,
    BOSCONIAN = 7,
    GALAXIAN = 8,
    DRAGONFLY = 9,
    MOSQUITO = 10,
    ENTERPRISE = 11,
    FIGHTER_EXPLOSION = 12,
    BEAM = 13,
    EXPLOSION = 14,
    BLUE_BULLET = 15,
    RED_BULLET = 16,
    BADGE1 = 17,
    BADGE5 = 18,
    BADGE10 = 19,
    BADGE20 = 20,
    BADGE30 = 21,
    BADGE50 = 22,
    NAMCO = 23
    SCORE_150 = 24,
    SCORE_400 = 25,
    SCORE_800 = 26,
    SCORE_1000 = 27,
    SCORE_1500 = 28,
    SCORE_1600 = 29,
    SCORE_2000 = 30,
    SCORE_3000 = 31


class Plan(IntEnum):
    DEAD = 0
    INIT = 1
    ALIVE = 2
    PATH = 3
    GOTO_GRID = 4
    ORIENT = 5
    GRID = 6
    DIVE_AWAY_LAUNCH = 7
    DIVE_AWAY = 8
    DIVE_ATTACK = 9
    DESCEND = 10
    HOME_OR_FULL_CIRCLE = 11
    FLUTTER = 12
    GOTO_BEAM = 13
    BEAM_ACTION = 14


class BeamState(IntEnum):
    OFF = 0,
    BOSS_SELECTED = 1,
    POSITION = 2,
    OPENING = 3,
    HOLD = 4,
    CLOSING = 5,
    CLOSED = 6


class CaptureState(IntEnum):
    OFF = 0
    FIGHTER_TOUCHED = 1,
    DISPLAY_CAPTURED = 2,
    HOLD = 3,
    FIGHTER_CAPTURED = 4,
    CAPTURE_COMPLETE = 5,
    DISPLAY_READY = 6,
    READY = 7,
    RESCUED = 8,
    SPINNING = 9,
    DOCKING = 10


COLOR_WHITE = pg.Color(206, 206, 206, 255)
COLOR_ROBIN = pg.Color(16, 230, 206, 255)
COLOR_RED = pg.Color(230, 16, 16, 255)
COLOR_BLUE = pg.Color(16, 16, 206, 255)
COLOR_YELLOW = pg.Color(230, 230, 16, 255)


class EntityData:
    # entity type, frame name, num of anim frames, num of sprite to create (all sprites are pre-alloced)
    def __init__(self, ent_type, frame_name, frame_numbers, sprite_numbers, shape_size=(0, 0)):
        # EntityType
        self.ent_type = ent_type

        # The frame name of this entity
        self.frame_name = frame_name

        # How many (animations) frames are available for this entity type
        self.frame_numbers = frame_numbers

        # How many sprites are available for this entity type
        self.sprite_numbers = sprite_numbers

        # where each entity type starts in game.sprites
        self.sprite_offset = 0

        # how many sprites of that entity-type are currenty used in self.sprites
        # used to get the next free sprite from game.sprites
        # 2 item, one for player1 and the other for player2
        self.sprites_used = [0, 0]

        # the shape size of this entity type (used for collision detection)
        self.shape_size = shape_size


class EntitiesService:
    def __init__(self):
        self.ent_data = {
            # 2 in-game ships + 15 for displaying lives following
            EntityType.FIGHTER: EntityData(EntityType.FIGHTER, "player", 0, 17),
            EntityType.CAPTURED_FIGHTER: EntityData(EntityType.CAPTURED_FIGHTER, "player_captured", 0, 1),
            EntityType.BOSS_GREEN: EntityData(EntityType.BOSS_GREEN, "boss_green", 2, 6),
            EntityType.BOSS_BLUE: EntityData(EntityType.BOSS_BLUE, "boss_blue", 2, 6),
            # 9*4=36 (chlngs = 10 waves @ 4/wave, 1 wave is cmndr green)
            EntityType.BUTTERFLY: EntityData(EntityType.BUTTERFLY, "butterfly", 2, 36, (13, 10)),
            EntityType.BEE: EntityData(EntityType.BEE, "bee", 2, 36, (13, 10)),
            EntityType.SCORPION: EntityData(EntityType.SCORPION, "scorpion", 2, 36),
            EntityType.BOSCONIAN: EntityData(EntityType.BOSCONIAN, "bosconian", 0, 16),
            EntityType.GALAXIAN: EntityData(EntityType.GALAXIAN, "galaxian", 0, 36),
            EntityType.DRAGONFLY: EntityData(EntityType.DRAGONFLY, "dragonfly", 0, 36),
            EntityType.MOSQUITO: EntityData(EntityType.MOSQUITO, "mosquito", 3, 36),
            EntityType.ENTERPRISE: EntityData(EntityType.ENTERPRISE, "enterprise", 0, 36),
            EntityType.FIGHTER_EXPLOSION: EntityData(EntityType.FIGHTER_EXPLOSION, "player_explosion", 4, 1),
            EntityType.BEAM: EntityData(EntityType.BEAM, "beam", 3, 1),
            EntityType.EXPLOSION: EntityData(EntityType.EXPLOSION, "explosion", 5, 4),
            EntityType.BLUE_BULLET: EntityData(EntityType.BLUE_BULLET, "blue_bullet", 0, 4, (3, 8)),
            EntityType.RED_BULLET: EntityData(EntityType.RED_BULLET, "red_bullet", 0, MAX_ENEMY_BULLETS, (3, 8)),
            EntityType.BADGE1: EntityData(EntityType.BADGE1, "badge1", 0, 4),
            EntityType.BADGE5: EntityData(EntityType.BADGE5, "badge5", 0, 1),
            EntityType.BADGE10: EntityData(EntityType.BADGE10, "badge10", 0, 1),
            EntityType.BADGE20: EntityData(EntityType.BADGE20, "badge20", 0, 1),
            EntityType.BADGE30: EntityData(EntityType.BADGE30, "badge30", 0, 1),
            EntityType.BADGE50: EntityData(EntityType.BADGE50, "badge50", 0, 5),
            EntityType.NAMCO: EntityData(EntityType.NAMCO, "namco", 0, 1),
            EntityType.SCORE_150: EntityData(EntityType.SCORE_150, "score-150", 0, 1),
            EntityType.SCORE_400: EntityData(EntityType.SCORE_400, "score-400", 0, 1),
            EntityType.SCORE_800: EntityData(EntityType.SCORE_800, "score-800", 0, 1),
            EntityType.SCORE_1000: EntityData(EntityType.SCORE_1000, "score-1000", 0, 1),
            EntityType.SCORE_1500: EntityData(EntityType.SCORE_1500, "score-1500", 0, 1),
            EntityType.SCORE_1600: EntityData(EntityType.SCORE_1600, "score-1600", 0, 1),
            EntityType.SCORE_2000: EntityData(EntityType.SCORE_2000, "score-2000", 0, 1),
            EntityType.SCORE_3000: EntityData(EntityType.SCORE_3000, "score-3000", 0, 1),
        }

    def get_entity_data(self, ent_type: EntityType) -> EntityData:
        return self.ent_data[ent_type]

    def get_sprite_numbers(self, ent_type: EntityType) -> int:
        return self.ent_data[ent_type].sprite_numbers

    def set_sprite_numbers(self, ent_type: EntityType, value: int):
        self.ent_data[ent_type].sprite_numbers = value

    def get_sprite_offset(self, ent_type: EntityType) -> int:
        return self.ent_data[ent_type].sprite_offset

    def set_sprite_offset(self, ent_type: EntityType, value: int):
        self.ent_data[ent_type].sprite_offset = value

    def get_sprites_used(self, ent_type: EntityType, player_idx: int) -> int:
        return self.ent_data[ent_type].sprites_used[player_idx]

    def set_sprites_used(self, ent_type: EntityType, player_idx: int, value: int):
        self.ent_data[ent_type].sprites_used[player_idx] = value

    def get_last_sprite_idx(self, ent_type: EntityType) -> int:
        """ Returns the last available sprite idx for the given entity type """
        return self.get_sprite_offset(ent_type) + self.get_sprite_numbers(ent_type) - 1

    def get_first_free_sprite_idx(self, ent_type: EntityType, player_idx: int) -> int:
        """ Returns the first free sprite idx for the given entity type and increment sprites_used """
        idx = self.get_sprite_offset(ent_type) + self.get_sprites_used(ent_type, player_idx)
        self.ent_data[ent_type].sprites_used[player_idx] += 1
        return idx


# text id, text string, percentage position, color, text alignment
g_texts_data = [
    (TEXT_1UP, '1UP', (7.5, 0.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_SCORE1P, '', (-3.00, 3.00), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_HIGH_SCORE, 'HIGH SCORE', (32.50, 0.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_20000, '20000', (43.00, 3.00), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_CREDIT, 'CREDIT', (3.75, 97.00), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_0, '0', (28.90, 97.00), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_GALAGA, 'GALAGA', (39.50, 11.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_DASH_SCORE, '__ SCORE __', (28.50, 19.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_50_100, '50    100', (43.00, 27.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_80_160, '80    160', (43.00, 33.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_2UP, '2UP', (82.50, 0.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_SCORE2P, '00', (71.75, 3.00), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_COPYRIGHT, '^ 1981 NAMCO LTD.', (21.00, 80.50), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_FIGHTER_CAPTURED, 'FIGHTER CAPTURED', (20.50, 52.50), COLOR_RED, TextAlignment.LEFT),
    (TEXT_GAME_OVER, 'GAME OVER', (36.00, 50.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_HEROES, 'THE GALACTIC HEROES', (15.00, 19.50), COLOR_BLUE, TextAlignment.LEFT),
    (TEXT_BEST_5, '__ BEST 5 __', (25.00, 39.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_SCORE, 'SCORE', (32.25, 55.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_NAME, 'NAME', (68.25, 55.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_1ST, '1ST', (11.50, 61.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_2ND, '2ND', (11.50, 66.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_3RD, '3RD', (11.50, 72.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_4TH, '4TH', (11.50, 77.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_5TH, '5TH', (11.50, 83.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SCORE_1, '20000', (25.15, 61.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SCORE_2, '20000', (25.15, 66.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SCORE_3, '20000', (25.15, 72.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SCORE_4, '20000', (25.15, 77.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SCORE_5, '20000', (25.15, 83.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_N_N, 'N.N', (71.50, 61.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_A_A, 'A.A', (71.50, 66.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_M_M, 'M.M', (71.50, 72.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_C_C, 'C.C', (71.50, 77.50), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_O_O, 'O.O', (71.50, 83.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_ENTER_INITIALS, 'ENTER YOUR INITIALS !', (15.00, 16.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_INITIALS_SCORE, 'SCORE', (22.00, 25.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_INITIALS_NAME, 'NAME', (64.50, 25.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_INITALS_SCORE_NUM, '20000', (18.45, 30.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_INITALS_INITIALS, 'AAA', (68.00, 30.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_TOP_5, 'TOP 5', (40.00, 50.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_PUSH_START, 'PUSH START BUTTON', (21.50, 36.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_1BONUS_FOR, '1ST BONUS FOR 20000 PTS', (14.50, 47.00), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_2BONUS_FOR, '2ND BONUS FOR 70000 PTS', (14.50, 55.50), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_FOR_BONUS, 'AND FOR EVERY 70000 PTS', (14.50, 64.00), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_PLAYER, 'PLAYER', (0.00, 47.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_PLAYER_NUM, '1', (0.00, 47.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_STAGE, 'STAGE', (36.00, 50.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_STAGE_NUM, '1', (58.00, 50.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_CHALLENGING_STAGE, 'CHALLENGING STAGE', (18.00, 50.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_READY, 'READY', (36.00, 50.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_RESULTS, '_RESULTS_', (32.00, 47.00), COLOR_RED, TextAlignment.LEFT),
    (TEXT_SHOTS_FIRED, 'SHOTS FIRED', (14.50, 55.50), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_SHOTS_FIRED_NUM, '0', (72.00, 55.50), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_HIT_MISS_RATIO, 'HIT-MISS RATIO', (14.50, 72.50), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_HIT_MISS_RATIO_NUM, '0.0 %', (72.00, 72.50), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_NUMBER_OF_HITS, 'NUMBER OF HITS', (0.00, 64.00), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_NUMBER_OF_HITS_NUM, '0', (0.00, 64.00), COLOR_YELLOW, TextAlignment.LEFT),
    (TEXT_BONUS, 'BONUS', (29.00, 58.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_BONUS_NUM, '100', (54.00, 58.00), COLOR_ROBIN, TextAlignment.LEFT),
    (TEXT_SPECIAL_BONUS, 'SPECIAL BONUS 10000 PTS', (50, 60), COLOR_YELLOW, TextAlignment.CENTER),
    (TEXT_PERFECT, 'PERFECT !', (50, 40), COLOR_RED, TextAlignment.CENTER),
    (TEXT_RAM_OK, 'RAM OK', (80.0, 90.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_ROM_OK, 'ROM OK', (80.0, 85.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_UPRIGHT, 'UPRIGHT', (80.0, 80.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_1_COIN_1_CREDIT, '1 COIN  1 CREDIT', (80.0, 75.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_3_FIGHTERS, '3 FIGHTERS', (80.0, 70.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_RANK_A, 'RANK  A', (80.0, 65.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_SOUND_00, 'SOUND 00', (80.0, 60.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_1ST_BONUS, '1ST BONUS 20000 PTS', (90.0, 50.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_2ND_BONUS, '2ND BONUS 70000 PTS', (90.0, 45.0), COLOR_WHITE, TextAlignment.LEFT),
    (TEXT_EVERY_BONUS, 'AND EVERY 70000 PTS', (90.0, 40.0), COLOR_WHITE, TextAlignment.LEFT)
]


# ------------------------------------------------------------------------------
# Spawn and path data
# The points for motion on a path.  Each path has a "mirror path" which is
# derived from the path data here so path indicies are 2x the indicies in the array.
# Odd numbered indicies indicate derived mirror paths
aPath_Top_Single = 0
aPath_Top_Double_Left = 1
aPath_Top_Double_Right = 2
aPath_Bottom_Single = 3
aPath_Bottom_Double_Out = 4
aPath_Bottom_Double_In = 5
aPath_Challenge_1_1 = 6
aPath_Challenge_1_2 = 7
aPath_Challenge_2_1 = 8
aPath_Challenge_2_2 = 9
aPath_Challenge_3_1 = 10
aPath_Challenge_3_2 = 11
aPath_Launch = 12
aPath_Bee_Attack = 13
aPath_Bee_Bottom_Circle = 14
aPath_Bee_Top_Circle = 15
aPath_Butterfly_Attack = 16
aPath_Boss_Attack = 17

PATH_TOP_SINGLE = 0
PATH_TOP_SINGLE_MIR = 1
PATH_TOP_DOUBLE_LEFT = 2
PATH_TOP_DOUBLE_LEFT_MIR = 3
PATH_TOP_DOUBLE_RIGHT = 4
PATH_TOP_DOUBLE_RIGHT_MIR = 5
PATH_BOTTOM_SINGLE = 6
PATH_BOTTOM_SINGLE_MIR = 7
PATH_BOTTOM_DOUBLE_OUT = 8
PATH_BOTTOM_DOUBLE_OUT_MIR = 9
PATH_BOTTOM_DOUBLE_IN = 10
PATH_BOTTOM_DOUBLE_IN_MIR = 11
PATH_CHALLENGE_1_1 = 12
PATH_CHALLENGE_1_1_MIR = 13
PATH_CHALLENGE_1_2 = 14
PATH_CHALLENGE_1_2_MIR = 15
PATH_CHALLENGE_2_1 = 16
PATH_CHALLENGE_2_1_MIR = 17
PATH_CHALLENGE_2_2 = 18
PATH_CHALLENGE_2_2_MIR = 19
PATH_CHALLENGE_3_1 = 20
PATH_CHALLENGE_3_1_MIR = 21
PATH_CHALLENGE_3_2 = 22
PATH_CHALLENGE_3_2_MIR = 23
PATH_LAUNCH = 24
PATH_LAUNCH_MIR = 25
PATH_BEE_ATTACK = 26
PATH_BEE_ATTACK_MIR = 27
PATH_BEE_BOTTOM_CIRCLE = 28
PATH_BEE_BOTTOM_CIRCLE_MIR = 29
PATH_BEE_TOP_CIRCLE = 30
PATH_BEE_TOP_CIRCLE_MIR = 31
PATH_BUTTERFLY_ATTACK = 32
PATH_BUTTERFLY_ATTACK_MIR = 33
PATH_BOSS_ATTACK = 34
PATH_BOSS_ATTACK_MIR = 35

gStartPath = [(0.0, 0.0) for x in range(aPath_Challenge_3_2 + 1)]
gPathData = [list() for x in range(aPath_Boss_Attack + 1)]

gStartPath[aPath_Top_Single] = (56.14, 3.30)
gStartPath[aPath_Top_Double_Left] = (56.27, 3.30)
gStartPath[aPath_Top_Double_Right] = (63.52, 3.30)
gStartPath[aPath_Bottom_Single] = (-3.00, 87.20)
gStartPath[aPath_Bottom_Double_Out] = (-3.00, 87.20)
gStartPath[aPath_Bottom_Double_In] = (-3.00, 81.47)
gStartPath[aPath_Challenge_1_1] = (41.91, 3.30)
gStartPath[aPath_Challenge_1_2] = (-3.00, 87.48)
gStartPath[aPath_Challenge_2_1] = (42.00, 3.30)
gStartPath[aPath_Challenge_2_2] = (-3.00, 86.50)
gStartPath[aPath_Challenge_3_1] = (42.60, 3.30)
gStartPath[aPath_Challenge_3_2] = (-3.00, 86.50)

gPathData[aPath_Top_Single] = [(0.00, 4.57), (-1.09, 3.60), (-2.92, 3.95), (-38.68, 30.55), (-2.07, 3.21),
                               (0.13, 3.00), (1.30, 3.49), (1.94, 2.14), (4.78, 2.71), (1.82, 1.07), (5.82, 0.10),
                               (2.84, -1.17), (2.98, -1.55), (1.68, -1.45), (3.49, -4.08), (0.13, -1.55)]
gPathData[aPath_Top_Double_Left] = [(0.00, 3.78), (-1.68, 4.85), (-3.75, 5.63), (-41.27, 29.77), (-3.36, 4.95),
                                    (-0.91, 2.33), (0.00, 4.26), (1.82, 2.72), (9.18, 7.86), (7.24, 3.00),
                                    (5.57, 0.29), (9.44, -3.58), (6.08, -5.14), (3.36, -4.85)]
gPathData[aPath_Top_Double_Right] = [(0.00, 3.00), (-0.13, 2.33), (-1.68, 4.08), (-3.75, 5.62), (-43.60, 33.08),
                                     (-0.91, 1.94), (-0.13, 1.35), (0.91, 3.59), (1.94, 2.72), (4.27, 2.81),
                                     (4.40, 1.36), (4.53, 0.39), (6.34, -3.01), (3.49, -4.75), (1.03, -2.72)]
gPathData[aPath_Bottom_Single] = [(3.13, 0.00), (2.59, -0.68), (4.52, -1.46), (9.06, -4.75), (12.94, -8.73),
                                  (8.53, -7.27), (3.24, -6.99), (0.00, -3.49), (-1.15, -3.38), (-3.14, -2.47),
                                  (-4.29, -0.90), (-4.29, 0.90), (-3.14, 2.47), (-1.15, 3.38), (1.15, 3.38),
                                  (3.14, 2.47), (4.29, 0.90), (4.29, -0.90), (3.14, -2.47), (1.15, -3.38)]
gPathData[aPath_Bottom_Double_Out] = [(6.75, 0.00), (15.40, -4.17), (11.51, -5.53), (10.09, -6.89), (9.44, -8.44),
                                      (1.69, -5.43), (0.00, -2.13), (-2.01, -5.25), (-5.49, -3.84), (-7.50, -1.41),
                                      (-7.50, 1.41), (-5.49, 3.84), (-2.01, 5.25), (2.01, 5.25), (5.49, 3.84),
                                      (7.50, 1.41), (7.50, -1.41), (5.49, -3.84), (2.01, -5.25)]
gPathData[aPath_Bottom_Double_In] = [(6.88, 0.00), (15.40, -4.17), (11.51, -5.53), (9.70, -7.17), (4.40, -6.02),
                                     (0.00, -3.97), (-1.21, -3.38), (-3.29, -2.47), (-4.50, -0.90), (-4.50, 0.90),
                                     (-3.29, 2.47), (-1.21, 3.38), (1.21, 3.38), (3.29, 2.47), (4.50, 0.90),
                                     (4.50, -0.90), (3.29, -2.47), (1.21, -3.38)]
gPathData[aPath_Challenge_1_1] = [(0.39, 27.35), (6.73, 22.79), (10.35, 19.89), (2.20, 3.39), (4.01, 2.04),
                                  (4.40, 1.94), (4.01, 0.68), (3.88, -1.07), (3.75, -2.04), (3.23, -3.10),
                                  (2.33, -3.59), (0.00, -3.59), (-1.03, -2.13), (-2.20, -2.52), (-2.46, -1.46),
                                  (-5.17, -2.52), (-6.73, -1.55), (-72.60, -29.51)]
gPathData[aPath_Challenge_1_2] = [(8.82, -0.57), (8.15, -1.36), (5.43, -1.17), (7.90, -2.23), (5.43, -1.94),
                                  (8.15, -4.07), (8.80, -4.66), (6.59, -4.07), (6.21, -4.27), (3.37, -4.07),
                                  (0.00, -24.83), (-4.01, -2.81), (-2.72, -0.97), (-2.20, 0.19), (-2.72, 2.04),
                                  (-2.19, 2.62), (-0.39, 1.94), (0.90, 20.85), (2.20, 1.84), (1.81, 1.26),
                                  (2.72, 0.58), (1.81, 0.49), (41.94, -40.49)]
gPathData[aPath_Challenge_2_1] = [(-0.02, 2.53), (0.12, 14.36), (1.23, 15.74), (1.36, 2.68), (5.93, 17.22),
                                  (1.97, 3.61), (0.06, 0.00), (0.05, -0.04), (-2.08, -3.57), (-5.93, -17.22),
                                  (-1.36, -2.68), (-1.23, -15.74), (-0.12, -14.36)]
gPathData[aPath_Challenge_2_2] = [(53.00, 0.00), (9.67, -0.95), (9.01, -2.80), (7.74, -4.45), (5.94, -5.80),
                                  (3.73, -6.76), (1.27, -7.25), (-1.27, -7.25), (-3.73, -6.76), (-5.94, -5.80),
                                  (-7.74, -4.45), (-9.01, -2.80), (-9.67, -0.95), (-9.67, 0.95), (-9.01, 2.80),
                                  (-7.74, 4.45), (-5.94, 5.80), (-3.73, 6.76), (-1.27, 7.25), (1.27, 7.25),
                                  (3.73, 6.76), (5.94, 5.80), (7.74, 4.45), (9.01, 2.80), (9.67, 0.95), (53.00, 0.00)]
gPathData[aPath_Challenge_3_1] = [(0.00, 40.18), (-1.93, 2.70), (-2.06, 3.19), (-3.09, 3.58), (-8.24, 6.76),
                                  (-22.39, 11.50), (-3.22, 1.54), (0.00, -1.54), (0.90, -1.55), (2.58, 0.20),
                                  (2.19, 0.28), (17.89, -8.59), (6.30, -4.84), (6.18, -4.92), (2.32, -3.29),
                                  (2.05, -3.57), (1.94, -5.12), (0.00, -43.11)]
gPathData[aPath_Challenge_3_2] = [(37.11, 0.00), (0.64, 0.00), (0.00, 0.00), (-0.52, 0.00), (-0.51, 0.00),
                                  (-5.41, 0.00), (-5.79, -1.48), (-4.12, -2.31), (-9.39, -7.54), (-2.45, -3.29),
                                  (-1.03, -4.05), (0.13, -9.96), (1.42, -10.04), (4.25, -12.18), (4.63, -5.51),
                                  (5.53, -4.83), (5.41, -2.80), (5.79, -1.25), (5.02, -0.10), (2.06, 1.06),
                                  (3.86, 3.96), (0.39, 3.39), (0.00, 26.57), (0.05, 0.05), (0.05, 0.00), (56.28, 0.00)]

# There is no StartPath for these
gPathData[aPath_Launch] = [(-0.67, -2.50), (-1.83, -1.83), (-2.50, -0.67), (-2.50, 0.67), (-1.83, 1.83), (-0.67, 2.50)]
gPathData[aPath_Bee_Attack] = [(1.55, 1.45), (42.30, 12.22), (8.67, 6.40), (4.53, 5.92), (5.17, 6.77)]
gPathData[aPath_Bee_Bottom_Circle] = [(-2.34, 6.56), (-6.41, 4.80), (-8.75, 1.76), (-8.75, -1.76), (-6.41, -4.80),
                                      (-2.34, -6.56)]
gPathData[aPath_Bee_Top_Circle] = [(-2.34, -6.56), (-6.40, -4.80), (-8.75, -1.76), (-8.75, 1.76), (-6.40, 4.80),
                                   (-2.34, 6.56)]
gPathData[aPath_Butterfly_Attack] = [(2.46, 2.53), (31.35, 13.80), (6.99, 6.02), (2.33, 3.31), (0.00, 4.56)]
gPathData[aPath_Boss_Attack] = [(0, 16), (0.67, 2.50), (1.83, 1.83), (2.50, 0.67), (2.50, -0.67), (1.83, -1.83),
                                (0.67, -2.50), (-0.67, -2.50), (-1.83, -1.83), (-2.50, -0.67), (-2.50, 0.67),
                                (-1.83, 1.83), (-0.67, 2.50), (53.44, 32.13), (1.32, 1.34), (0.93, 1.23), (0.26, 1.96),
                                (0.13, 7.92), (-0.79, 1.34), (-1.19, 1.23), (-1.46, 1.24), (-1.85, 0.92),
                                (-1.58, 1.03), (-1.59, 1.13), (-1.46, 0.83), (-0.53, 1.03)]

# numbers from 4 to 43 (5 waves * 8 enemies = 40 positions on the grid)
# positions 0-3 are reserved for captured fighter
# 20 position on the left side, the other 20 on the right side

# [wave, side, enemy position in the grid]
# declare a 3d array with the following sizes: a[5][2][4]
gSpawn_order = [[[0 for z in range(4)] for y in range(2)] for x in range(5)]
gSpawn_order[0][0] = [11, 12, 19, 20]
gSpawn_order[1][0] = [4, 5, 6, 7]
gSpawn_order[2][0] = [14, 22, 8, 16]
gSpawn_order[3][0] = [30, 40, 26, 36]
gSpawn_order[4][0] = [24, 34, 32, 42]

gSpawn_order[0][1] = [28, 29, 38, 39]
gSpawn_order[1][1] = [10, 13, 18, 21]
gSpawn_order[2][1] = [15, 23, 9, 17]
gSpawn_order[3][1] = [31, 41, 27, 37]
gSpawn_order[4][1] = [25, 35, 33, 43]

# col position relative to grid
gGrid_cols = [
    3, 4, 5, 6,
    3, 4, 5, 6,
    1, 2, 3, 4, 5, 6, 7, 8,
    1, 2, 3, 4, 5, 6, 7, 8,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# row position relative to grid
gGrid_rows = [
    0, 0, 0, 0,
    1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

gMirror = [
    0, 0, 1, 1,
    0, 0, 1, 1,
    0, 0, 0, 0, 1, 1, 1, 1,
    0, 0, 0, 0, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

# gSpawnKind indicates what type of enemy to spawn
# (repeats 0, 1, 0, 1, etc.) at wave or challenge
gSpawn_kind = [[0 for y in range(2)] for x in range(5)]
# wave-number, left, right
gSpawn_kind[0] = [EntityType.BUTTERFLY, EntityType.BEE]  # wave 1
gSpawn_kind[1] = [EntityType.BOSS_GREEN, EntityType.BUTTERFLY]  # wave 2
gSpawn_kind[2] = [EntityType.BUTTERFLY, EntityType.BUTTERFLY]  # wave 3
gSpawn_kind[3] = [EntityType.BEE, EntityType.BEE]  # wave 4
gSpawn_kind[4] = [EntityType.BEE, EntityType.BEE]  # wave 5

# ------------------------------------------------------------------------------
#  gPathIndicies indicates onto which path a newly spawned enemy should be put
#
#  stage 1  0001 stageIndex 2
#  stage 2  0010 stageIndex 1
#  stage 3  0011 stageIndex 3 challengeIndex = 5
#  stage 4  0100 stageIndex 0
#  stage 5  0101 stageIndex 1
#  stage 6  0110 stageIndex 2
#  stage 7  0111 stageIndex 4 challengeIndex = 10
#  stage 8  1000 stageIndex 0
#  stage 9  1001 stageIndex 1
#  stage 10 1010 stageIndex 2
#  stage 11 1011 stageIndex 5 challengeIndex = 15
#  stage 12 1100 stageIndex 0
#  stage 13 1101 stageIndex 1
#  stage 14 1110 stageIndex 2
#
# stageIndex, wave, side
gPath_indicies = [[[0 for z in range(2)] for y in range(5)] for x in range(6)]

# Stage 4 and up
gPath_indicies[0][0] = [PATH_TOP_SINGLE_MIR, PATH_TOP_SINGLE]
gPath_indicies[0][1] = [PATH_BOTTOM_SINGLE, PATH_BOTTOM_SINGLE_MIR]
gPath_indicies[0][2] = [PATH_BOTTOM_SINGLE, PATH_BOTTOM_SINGLE_MIR]
gPath_indicies[0][3] = [PATH_TOP_SINGLE_MIR, PATH_TOP_SINGLE]
gPath_indicies[0][4] = [PATH_TOP_SINGLE_MIR, PATH_TOP_SINGLE]

# stage 2 and up
gPath_indicies[1][0] = [PATH_TOP_DOUBLE_RIGHT, PATH_TOP_DOUBLE_RIGHT_MIR]
gPath_indicies[1][1] = [PATH_BOTTOM_DOUBLE_OUT, PATH_BOTTOM_DOUBLE_IN]
gPath_indicies[1][2] = [PATH_BOTTOM_DOUBLE_OUT_MIR, PATH_BOTTOM_DOUBLE_IN_MIR]
gPath_indicies[1][3] = [PATH_TOP_DOUBLE_LEFT, PATH_TOP_DOUBLE_RIGHT]
gPath_indicies[1][4] = [PATH_TOP_DOUBLE_LEFT_MIR, PATH_TOP_DOUBLE_RIGHT_MIR]

# Stage 0, 1 and up
gPath_indicies[2][0] = [PATH_TOP_SINGLE_MIR, PATH_TOP_SINGLE]
gPath_indicies[2][1] = [PATH_BOTTOM_SINGLE, PATH_BOTTOM_SINGLE]
gPath_indicies[2][2] = [PATH_BOTTOM_SINGLE_MIR, PATH_BOTTOM_SINGLE_MIR]
gPath_indicies[2][3] = [PATH_TOP_SINGLE, PATH_TOP_SINGLE]
gPath_indicies[2][4] = [PATH_TOP_SINGLE_MIR, PATH_TOP_SINGLE_MIR]

# Special levels will go here
# Challenge 1
gPath_indicies[3][0] = [PATH_CHALLENGE_1_1, PATH_CHALLENGE_1_1_MIR]
gPath_indicies[3][1] = [PATH_CHALLENGE_1_2, PATH_CHALLENGE_1_2]
gPath_indicies[3][2] = [PATH_CHALLENGE_1_2_MIR, PATH_CHALLENGE_1_2_MIR]
gPath_indicies[3][3] = [PATH_CHALLENGE_1_1_MIR, PATH_CHALLENGE_1_1_MIR]
gPath_indicies[3][4] = [PATH_CHALLENGE_1_1, PATH_CHALLENGE_1_1]

# Challenge 2
gPath_indicies[4][0] = [PATH_CHALLENGE_2_1, PATH_CHALLENGE_2_1_MIR]
gPath_indicies[4][1] = [PATH_CHALLENGE_2_2, PATH_CHALLENGE_2_2_MIR]
gPath_indicies[4][2] = [PATH_CHALLENGE_2_2, PATH_CHALLENGE_2_2_MIR]
gPath_indicies[4][3] = [PATH_CHALLENGE_2_1_MIR, PATH_CHALLENGE_2_1_MIR]
gPath_indicies[4][4] = [PATH_CHALLENGE_2_1, PATH_CHALLENGE_2_1]

# Challenge 3
gPath_indicies[5][0] = [PATH_CHALLENGE_3_1_MIR, PATH_CHALLENGE_3_1]
gPath_indicies[5][1] = [PATH_CHALLENGE_3_2, PATH_CHALLENGE_3_2_MIR]
gPath_indicies[5][2] = [PATH_CHALLENGE_3_2, PATH_CHALLENGE_3_2_MIR]
gPath_indicies[5][3] = [PATH_CHALLENGE_3_1_MIR, PATH_CHALLENGE_3_1]
gPath_indicies[5][4] = [PATH_CHALLENGE_3_1_MIR, PATH_CHALLENGE_3_1]

gAttack_order = [
    8, 24, 16, 34, 15, 33, 23, 43,
    9, 25, 17, 35, 14, 32, 22, 42,
   10, 26, 18, 36, 13, 31, 21, 41,
   11, 27, 19, 37, 12, 30, 20, 40,
   28, 38, 29, 39]


class Score:
    def __init__(self):
        self.name = ''
        self.score = 0


class Leaderboard:
    filename = os.path.join(os.path.expanduser('~'), 'pyjam-galaga_hiscores.txt')

    def __init__(self):
        self.high_scores = [Score() for x in range(5)]

        # there are used to enter a highscore
        self.edit_letter = 0
        self.edit_score = 0
        self.entry = Score()

    def save(self):
        f = open(self.filename, 'w')
        for hi_score in self.high_scores:
            f.write(f'{hi_score.name},{hi_score.score}\n')
        f.close()

    def load(self):
        f = open(self.filename, 'r')
        for hi_score in self.high_scores:
            line = f.readline()
            items = line.split(',')
            hi_score.name = items[0]
            hi_score.score = int(items[1])
        f.close()


# ----------------------------------------------
# SFX DATA
# ----------------------------------------------
SOUND_BEAM = 'beam'
SOUND_BEAM_CAPTURED = 'beam-captured'
SOUND_BREATHING_TIME = 'breathing-time'
SOUND_CAPTURED_FIGHTER_DESTROYED = 'captured-fighter-destroyed'
SOUND_CAPTURED_FIGHTER_RESCUED = 'captured-fighter-rescued'
SOUND_CHALLENGE_STAGE = 'challenge-stage'
SOUND_CHALLENGE_BONUS = 'challenge-bonus'
SOUND_CHALLENGE_PERFECT = 'challenge-perfect'
SOUND_COIN_DROPPED = 'coin-dropped'
SOUND_DANGER = 'danger'
SOUND_DIVE_ATTACK = 'dive-attack'
SOUND_EXTRA_LIFE = 'extra-life'
SOUND_HALL_OF_FAME = 'hall-of-fame'
SOUND_HIGHSCORE_END = 'highscore-end'
SOUND_HIGHSCORE_LOOP = 'highscore-loop'
SOUND_HIT_BEE = 'hit-bee'
SOUND_HIT_BUTTERFLY = 'hit-butterfly'
SOUND_HIT_COMMANDER_BLUE = 'hit-commander-blue'
SOUND_HIT_COMMANDER_GREEN = 'hit-commander-green'
SOUND_PLAYER_CAPTURED = 'player-captured'
SOUND_PLAYER_DIE = 'player-die'
SOUND_PLAYER_SHOOT = 'player-shoot'
SOUND_STAGE_ICON = 'stage-icon'
SOUND_START = 'start'

g_sfx = [
    SOUND_BEAM,
    SOUND_BEAM_CAPTURED,
    SOUND_BREATHING_TIME,
    SOUND_CAPTURED_FIGHTER_DESTROYED,
    SOUND_CAPTURED_FIGHTER_RESCUED,
    SOUND_CHALLENGE_STAGE,
    SOUND_CHALLENGE_BONUS,
    SOUND_CHALLENGE_PERFECT,
    SOUND_COIN_DROPPED,
    SOUND_DANGER,
    SOUND_DIVE_ATTACK,
    SOUND_EXTRA_LIFE,
    SOUND_HALL_OF_FAME,
    SOUND_HIGHSCORE_END,
    SOUND_HIGHSCORE_LOOP,
    SOUND_HIT_BEE,
    SOUND_HIT_BUTTERFLY,
    SOUND_HIT_COMMANDER_BLUE,
    SOUND_HIT_COMMANDER_GREEN,
    SOUND_PLAYER_CAPTURED,
    SOUND_PLAYER_DIE,
    SOUND_PLAYER_SHOOT,
    SOUND_STAGE_ICON,
    SOUND_START
]

g_kill_sound = {
    EntityType.FIGHTER: SOUND_PLAYER_DIE,
    EntityType.CAPTURED_FIGHTER: SOUND_CAPTURED_FIGHTER_DESTROYED,
    EntityType.ENTERPRISE: SOUND_HIT_BEE,
    EntityType.BOSS_GREEN: SOUND_HIT_COMMANDER_GREEN,
    EntityType.BOSS_BLUE: SOUND_HIT_COMMANDER_BLUE,
    EntityType.BUTTERFLY: SOUND_HIT_BUTTERFLY,
    EntityType.BEE: SOUND_HIT_BEE,
    EntityType.GALAXIAN: SOUND_HIT_BEE,
    EntityType.SCORPION: SOUND_HIT_BEE,
    EntityType.BOSCONIAN: SOUND_HIT_BEE,
    EntityType.DRAGONFLY: SOUND_HIT_BEE,
    EntityType.MOSQUITO: SOUND_HIT_BEE,
}
