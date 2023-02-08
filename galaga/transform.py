import copy
from enum import IntEnum

from pyjam.constants import ASSET_SERVICE
from pyjam.sprites.animation import Animation2D

from galaga_data import *


class Transform:
    class State(IntEnum):
        OFF = 0
        BLINK = 1,
        TRANSFORM = 2,
        DONE = 3,
        RESET = 4

    def __init__(self, enemy):
        self.__enemy = enemy
        # transform state
        self.__state = Transform.State.OFF
        # transform timer
        self.__timer = 0.0
        # saved anim
        self.__saved_anim = None

    @property
    def enemy(self):
        return self.__enemy

    @property
    def game(self):
        return self.enemy.game

    @property
    def state(self) -> State:
        return self.__state

    @state.setter
    def state(self, value: State):
        self.__state = value

    @property
    def timer(self) -> float:
        return self.__timer

    @timer.setter
    def timer(self, value):
        self.__timer = value

    @property
    def saved_anim(self):
        return self.__saved_anim

    @saved_anim.setter
    def saved_anim(self, value):
        self.__saved_anim = value

    def update(self):
        assets_sp_sheet = self.game.services[ASSET_SERVICE].get('textures/galaga-spritesheet')
        if self.state == Transform.State.BLINK:
            if self.timer == 0.0:
                # change the animation of bee or butterfly
                self.saved_anim = self.enemy.sprite.get_animation()
                animation = Animation2D()
                animation.add_frame(assets_sp_sheet.frames['bee_1'])
                animation.add_frame(assets_sp_sheet.frames['bee_scorpion_1'])
                animation.add_frame(assets_sp_sheet.frames['bee_2'])
                animation.add_frame(assets_sp_sheet.frames['bee_scorpion_2'])
                self.enemy.sprite.set_animation(animation)
                self.enemy.sprite.play(fps=4, loop=True)
                self.game.sfx_play(SOUND_TRANSFORM)
            else:
                self.timer += self.game.delta_time
                if self.timer > 2.0:
                    self.state = Transform.State.TRANSFORM
        elif self.state == Transform.State.TRANSFORM:
            # restore bee or butterly animation and hide the sprite
            self.enemy.sprite.set_animation(self.saved_anim)
            self.enemy.sprite.visible = False

            # clone the enemy
            kind = EntityType.SCORPION
            new_enemy = copy.copy(self.enemy)
            new_enemy.kind = kind
            new_enemy.sprite = self.game.get_first_free_sprite_by_ent_type(kind, self.game.current_player_idx)
            new_enemy.sprite.visible = True

            new_enemy.position_index = self.enemy.position
            new_enemy.plan = self.enemy.plan
            new_enemy.next_plan = self.enemy.next_plan
            new_enemy.attack_index = self.enemy.attack_index
            new_enemy.cargo_index = self.enemy.cargo_index
            new_enemy.x = self.enemy.x
            new_enemy.y = self.enemy.y
            new_enemy.rotation = self.enemy.rotation
            new_enemy.path_index = self.enemy.path_index
            new_enemy.point_index = self.enemy.point_index
            self.game.enemies[self.game.current_player_idx][new_enemy.position_index] = new_enemy

            self.state = Transform.State.DONE
        elif self.state == Transform.State.DONE:
            pass
        elif self.state == Transform.State.RESET:
            new_enemy = self.game.enemy_at(self.enemy.position_index)
            new_enemy.sprite.visible = False

            self.game.enemies[self.game.current_player_idx][new_enemy.position_index] = self.enemy
            self.enemy.sprite.visible = (new_enemy.Plan != Plan.DEAD)

            self.state = Transform.State.OFF
