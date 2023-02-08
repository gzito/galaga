import glm

from pyjam.application import GameState, pc2v

from galaga_data import *


class AttractState(GameState):
    class Substate(IntEnum):
        TITLE = 1,
        SHOW_VALUES = 2,
        SHOW_COPYRIGHT = 3,
        SHOW_PLAY = 4,
        SHOW_SCORES = 5,
        HAVE_CREDIT = 6

    def __init__(self, game, substate=None):
        super().__init__(game)
        self.__game = game
        self.__state_timer = 0.0
        self.__spawner = None
        if substate is None:
            self.__substate = AttractState.Substate.TITLE
        else:
            self.__substate = substate
        self.__scratch1 = 0

    @property
    def substate(self):
        return self.__substate

    @substate.setter
    def substate(self, new_state):
        self.__substate = new_state
        self.__scratch1 = 0
        self.__state_timer = 0.0

    def enter(self):
        # Show 1UP, HIGH SCORE and initial high score
        self.__game.set_text_range_visible(TEXT_1UP, TEXT_20000, True)
        self.__game.stars_svc.enable()

    def update(self):
        self.do_attract_sequence()
        if (self.game.start == 1 and self.game.num_credits) or (self.game.start == 2 and self.game.num_credits > 1):
            self.game.num_players = self.game.start
            self.game.use_credits()
            self.game.set_text_range_visible(TEXT_GALAGA, TEXT_END_GAME_TEXT, False)
            self.game.set_sprite_range_visible(0, len(self.game.sprites) - 1, False)
            self.game.change_state(self.game.instantiate_state('PlayingState'))

    def do_attract_sequence(self):
        self.__state_timer -= self.__game.delta_time

        if self.__substate == AttractState.Substate.TITLE:
            if self.__state_timer <= 0.0:
                self.__state_timer = TIME_TO_REVEAL
                self.__scratch1 += 1
                if not self.do_attract_title():
                    self.substate = AttractState.Substate.SHOW_VALUES
        elif self.__substate == AttractState.Substate.SHOW_VALUES:
            sprite = self.game.get_first_sprite_by_ent_type(EntityType.FIGHTER)
            sprite.position = pc2v(glm.vec2(50, ((ORIGINAL_Y_CELLSF - 3.0) / ORIGINAL_Y_CELLSF) * 100.0))
            sprite.visible = True
            self.substate = AttractState.Substate.SHOW_COPYRIGHT
        elif self.__substate == AttractState.Substate.SHOW_COPYRIGHT:
            if self.__scratch1 == 0:
                self.game.get_first_sprite_by_ent_type(EntityType.FIGHTER).visible = False
                self.game.get_first_sprite_by_ent_type(EntityType.NAMCO).visible = True
                self.game.texts[TEXT_COPYRIGHT].visible = True
                self.__state_timer = HOLD_COPYRIGHT
                self.__scratch1 = 1

            if self.__scratch1 == 1 and self.__state_timer < 0.0:
                self.game.set_sprite_range_visible(0, len(self.game.sprites) - 1, False)
                self.game.set_text_range_visible(TEXT_GALAGA, TEXT_COPYRIGHT, False)
                self.substate = AttractState.Substate.SHOW_PLAY
        elif self.__substate == AttractState.Substate.SHOW_PLAY:
            if self.__scratch1 == 0:
                self.game.texts[TEXT_FIGHTER_CAPTURED].visible = True
                self.__state_timer = HOLD_COPYRIGHT
                self.__scratch1 = 1

            if self.__scratch1 == 1 and self.__state_timer < 0.0:
                self.game.texts[TEXT_FIGHTER_CAPTURED].visible = False
                self.game.texts[TEXT_GAME_OVER].visible = True
                self.__state_timer = HOLD_HIGHSCORE - HOLD_COPYRIGHT
                self.__scratch1 = 2

            if self.__scratch1 == 2 and self.__state_timer < 0.0:
                self.game.texts[TEXT_GAME_OVER].visible = False
                self.substate = AttractState.Substate.SHOW_SCORES
        elif self.__substate == AttractState.Substate.SHOW_SCORES:
            if self.__scratch1 == 0:
                self.game.set_text_range_visible(TEXT_HEROES, TEXT_O_O, True)
                self.__state_timer = HOLD_HIGHSCORE
                self.__scratch1 = 1

            if self.__scratch1 == 1 and self.__state_timer < 0.0:
                self.game.set_text_range_visible(TEXT_HEROES, TEXT_O_O, False)
                self.substate = AttractState.Substate.TITLE
        elif self.__substate == AttractState.Substate.HAVE_CREDIT:
            self.do_attract_credits_in()

    def do_attract_title(self):
        if self.__scratch1 == 1:
            self.game.set_text_range_visible(TEXT_CREDIT, TEXT_0, True)
        elif self.__scratch1 - 1 <= TEXT_2UP - TEXT_GALAGA:
            self.game.texts[TEXT_GALAGA - 2 + self.__scratch1].visible = True

        if self.__scratch1 == 4:
            sprite = self.game.get_first_sprite_by_ent_type(EntityType.BEE)
            sprite.position = pc2v(glm.vec2(26.5, 28.5))
            sprite.angle = 0
            sprite.visible = True
        elif self.__scratch1 == 5:
            sprite = self.game.get_first_sprite_by_ent_type(EntityType.BUTTERFLY)
            sprite.position = pc2v(glm.vec2(26.5, 34.5))
            sprite.angle = 0
            sprite.visible = True
        elif self.__scratch1 == 6:
            sprite = self.game.get_first_sprite_by_ent_type(EntityType.BOSS_GREEN)
            sprite.position = pc2v(glm.vec2(50.0, 45))
            sprite.angle = 0
            sprite.visible = True
        elif self.__scratch1 == 7:
            for i in range(1, 5):
                sprite = self.game.get_sprite_at_by_ent_type(EntityType.BOSS_GREEN, i)
                sprite.position = pc2v(glm.vec2(i * (100.0 / 5.0), 52))
                sprite.angle = 0
                sprite.visible = True
        elif self.__scratch1 == 8:
            pos = [10.0, 11.0, 13.0]
            for i in range(1, 4):
                sprite = self.game.get_sprite_at_by_ent_type(EntityType.BUTTERFLY, i)
                sprite.position = pc2v(glm.vec2(pos[i - 1] * (100.0 / 15.0), 57.0))
                sprite.angle = 0
                sprite.visible = True
        elif self.__scratch1 == 9:
            return 0

        return 1

    def do_attract_credits_in(self):
        if not self.__scratch1:
            self.game.set_sprite_range_visible(0, self.game.ent_svc.get_sprite_offset(EntityType.RED_BULLET), False)
            self.game.set_text_range_visible(TEXT_GALAGA, TEXT_END_GAME_TEXT, False)
            self.game.set_text_range_visible(TEXT_PUSH_START, TEXT_FOR_BONUS, True)
            self.game.set_text_range_visible(TEXT_COPYRIGHT, TEXT_COPYRIGHT, True)
            for i in range(1, 4):
                sprite = self.game.get_sprite_at_by_ent_type(EntityType.FIGHTER, i)
                sx = self.game.texts[TEXT_1BONUS_FOR + i - 1].position.x
                sprite.scale = glm.vec2(1.0, 1.0)
                sx -= sprite.width
                syd = self.game.texts[TEXT_1BONUS_FOR + i - 1].size.y / 2.0
                sprite.position = glm.vec2(sx, self.game.texts[TEXT_1BONUS_FOR + i - 1].position.y + syd)
                sprite.visible = True

            self.__scratch1 += 1
