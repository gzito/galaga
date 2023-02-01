import glm

from pyjam.application import GameState, Game, pcx2vx, pcy2vy, pc2v, vx2pcx, vy2pcy
from galaga_data import *
from entities import create_entity
from pyjam.constants import ASSET_SERVICE
from pyjam.sprite import Sprite


class TestPath(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.entity = None
        self.moving = False
        self.fast_spawn = self.game.fast_spawn
        self.sprites_list = []

        self.entity_kind = EntityType.BOSS_GREEN
        self.position_index = 5
        self.path_indexes = [PATH_LAUNCH + gMirror[self.position_index],
                             PATH_BOSS_ATTACK + gMirror[self.position_index]]

    def enter(self):
        self.game.fast_spawn = False
        self.entity = create_entity(self.entity_kind)
        self.entity.plan = Plan.GOTO_GRID
        self.entity.position_index = self.position_index
        self.entity.x = pcx2vx(20)
        self.entity.y = pcy2vy(20)
        self.entity.shots_to_fire = 0
        self.entity.sprite.visible = True
        self.game.player().stage = 1
        self.game.bug_attack_speed = \
            BUG_ATTACK_SPEED_BASE + \
            ((BUG_ATTACK_SPEED_MAX - BUG_ATTACK_SPEED_BASE) / BUG_ATTACK_SPEED_WINDOW) * \
            (self.game.player().stage % BUG_ATTACK_SPEED_WINDOW)

    def handle_input(self):
        if self.game.key_pressed(pg.K_y) and not self.moving:
            self.entity.plan = Plan.PATH
            self.entity.path_index = self.path_indexes[0]
            self.entity.next_plan = Plan.PATH
            self.entity.next_path_point()
            self.trace_path()
            self.moving = True

        if self.game.mouse_button_pressed(0):
            pos = [self.entity.x, self.entity.y]
            path_idx = self.path_indexes[-1]
            index = path_idx >> 1
            coords = gPathData[index]

            for path_idx in self.path_indexes:
                index = path_idx >> 1
                for coord in gPathData[index]:
                    pos[0] += coord[0]
                    pos[1] += coord[1]

            mpos = self.game.screen_to_world(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
            coords.append((round(vx2pcx(mpos.x)-pos[0], 2), round(vy2pcy(mpos.y)-pos[1], 2)))
            print(coords)

        if self.game.mouse_button_pressed(2):
            path_idx = self.path_indexes[-1]
            index = path_idx >> 1
            coords = gPathData[index]
            coords.pop()

    def update(self):
        self.game.move_bullets()
        self.entity.update(self.game.delta_time)
        if self.moving and self.entity.plan == Plan.ORIENT:
            self.moving = False

    def trace_path(self):
        # trace the path
        for i in self.sprites_list:
            Game.instance.sprites.remove(i)
        self.sprites_list.clear()

        frame = Game.instance.services[ASSET_SERVICE].get('textures/star')

        pos = [self.entity.x, self.entity.y]
        for path_idx in self.path_indexes:
            index = path_idx >> 1
            if index == aPath_Bee_Bottom_Circle:
                pos[1] += 81.0 - pos[1]
            for coord in gPathData[index]:
                sprite = Sprite(frame)
                sprite.size = glm.vec2(1, 1)
                sprite.layer_depth = 0.1
                sprite.position = pc2v(glm.vec2(pos[0] + coord[0], pos[1] + coord[1]))
                pos[0] += coord[0]
                pos[1] += coord[1]
                sprite.color = pg.Color('red')
                self.sprites_list.append(sprite)
                Game.instance.sprites.append(sprite)

    def exit(self):
        self.entity.sprite.visible = False
        self.game.fast_spawn = self.fast_spawn
        for i in self.sprites_list:
            Game.instance.sprites.remove(i)
        self.sprites_list.clear()



