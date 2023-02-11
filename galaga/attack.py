import random

from galaga_data import *
from pyjam.application import Game


class Attackers:
    @property
    def game(self):
        return Game.instance

    def __init__(self):
        # max 2 attackers
        self.__attackers = [-1, -1]
        self.__num_attackers = 0

    def count(self):
        return self.__num_attackers

    def clear_all(self):
        """ clear all attackers slots """
        for i in range(len(self.__attackers)):
            self.clear_at(i)
        self.__num_attackers = 0

    def get_at(self, idx):
        return self.__attackers[idx]

    def insert_from(self, from_idx, position_in_the_grid):
        """ add an attacker at the first available slot starting from the index from_idx """
        for i in range(from_idx, len(self.__attackers)):
            if self.__attackers[i] == -1:
                self.__attackers[i] = position_in_the_grid
                self.game.enemy_at(position_in_the_grid).attack_index = i
                self.__num_attackers += 1
                break

    def append(self, position_in_the_grid):
        """ append an attacker """
        self.__attackers[self.__num_attackers] = position_in_the_grid
        self.game.enemy_at(position_in_the_grid).attack_index = self.__num_attackers
        self.__num_attackers += 1

    def clear_at(self, idx):
        """ clear the attacker at the given slot index """
        position = self.__attackers[idx]
        if position != -1:
            self.__attackers[idx] = -1
            self.__num_attackers -= 1


class AttackService:
    def __init__(self, game):
        self.__game = game

        self.attackers = Attackers()

        # True if it is ready for attack, otherwise False
        self.__bugs_attack = False
        # -1 = empty or # is grid-position

        # position index of the boss making beam, -1 none
        self.__beam_boss_idx = -1

        # position index of the boss bringing cargo, -1 none
        self.__cargo_boss_idx = -1

        # make a beam when is 2 -- if 0 or 1 => don't make a beam
        self.__beam_ready = 1

        # timer for next attack
        self.__attack_delay_timer = 0.0

        # last selected boss
        self.last_selected_boss = 7

    @property
    def game(self):
        return self.__game

    @property
    def bugs_attack(self) -> bool:
        return self.__bugs_attack

    @bugs_attack.setter
    def bugs_attack(self, value: bool):
        self.__bugs_attack = value

    @property
    def beam_ready(self):
        return self.__beam_ready

    @beam_ready.setter
    def beam_ready(self, value):
        self.__beam_ready = value

    @property
    def beam_boss_idx(self):
        return self.__beam_boss_idx

    @beam_boss_idx.setter
    def beam_boss_idx(self, value):
        self.__beam_boss_idx = value

    @property
    def cargo_boss_idx(self):
        return self.__cargo_boss_idx

    @cargo_boss_idx.setter
    def cargo_boss_idx(self, value):
        self.__cargo_boss_idx = value

    @property
    def delay_timer(self):
        return self.__attack_delay_timer

    @delay_timer.setter
    def delay_timer(self, value):
        self.__attack_delay_timer = value

    def decr_delay_timer(self, delta_time):
        self.__attack_delay_timer -= delta_time

    # try to select al least 2 attackers
    def attack_ready(self) -> bool:
        if self.game.player().spawn_active:
            return False
        if not self.game.quiescence:
            return False

        self.game.make_beam = BeamState.OFF
        self.beam_ready = 0

        # prime the attack structure with 2 attackers, not bosses, hence start looking from position 8
        self.attackers.clear_all()
        for position in gAttack_order:
            if self.attackers.count() < 2:
                if self.game.enemy_at(position).plan == Plan.GRID:
                    self.attackers.append(position)
            else:
                break

        return True

    def choose_attacker(self):
        player = self.game.player()

        # while the capture sequence is active, disable attackers
        if player.capture_state != CaptureState.OFF and player.capture_state != CaptureState.READY:
            return

        self.decr_delay_timer(self.game.delta_time)

        if self.delay_timer < 0.0:
            # only allow 2 at a time
            if self.attackers.count() < 2:
                # try to pick a boss
                if self.cargo_boss_idx == -1:
                    position = self.choose_next_boss_idx()
                    if position != -1:
                        boss_entity = self.game.enemy_at(position)
                        if boss_entity.plan == Plan.GRID:
                            self.attackers.insert_from(0, position)

                            # See if this boss should go make a beam
                            if self.can_make_beam(self.game.player()):
                                self.game.make_beam = BeamState.BOSS_SELECTED
                                self.beam_boss_idx = boss_entity.position_index
                                self.beam_ready = 0
                            else:
                                boss_entity.cargo.clear_all()

                                # See if there's cargo to take and set those ships up on a launch plan as well
                                # if this boss is a captor => there should be a captured fighter in the grid
                                if boss_entity.is_captor():
                                    pos_idx = player.captured_fighter.position_index
                                    boss_entity.cargo.insert_from(2, pos_idx)
                                    player.captured_fighter.set_cargo_boss(boss_entity)
                                    self.cargo_boss_idx = boss_entity.position_index

                                loaded = 0
                                for i in range(3):
                                    pos_idx = position + 5 + i
                                    cargo_entity = self.game.enemy_at(pos_idx)
                                    if cargo_entity.plan == Plan.GRID:
                                        loaded += 1
                                        boss_entity.cargo.insert_from(0, pos_idx)
                                        cargo_entity.set_cargo_boss(boss_entity)
                                        self.cargo_boss_idx = boss_entity.position_index
                                    if loaded == 2:
                                        break

                                self.beam_ready += 1

            # after boss pick, if still a slot, try to pick a bee or butterfly
            if self.cargo_boss_idx == -1:
                if self.attackers.count() < 2:
                    for position in gAttack_order:
                        # if idle
                        if self.game.enemy_at(position).plan == Plan.GRID:
                            self.attackers.insert_from(0, position)
                            # Exit loop as an enemy was put in a slot
                            break

                # if there is the captured fighter without its captor boss
                if player.captured_fighter is not None and player.get_captor_boss() is None:
                    # if still a free slot, select it as an attacker
                    if self.attackers.count() < 2:
                        position = player.captured_fighter.position_index
                        if player.captured_fighter.plan == Plan.GRID:
                            self.attackers.insert_from(0, position)

            # launch any attackers that haven't launched yet
            # This is done as a second part so that the initial primed 2 non-boss
            # attackers will get launched in this way
            for i in range(2):
                position = self.attackers.get_at(i)
                if position != -1:
                    # is this enemy idle or has it launched ?
                    enemy = self.game.enemy_at(position)
                    if enemy.plan == Plan.GRID:
                        # Make it launch if it was still idle
                        kind = enemy.kind
                        a_boss = enemy.is_boss_kind()
                        # if attacker is a boss
                        if a_boss:
                            if self.game.make_beam == BeamState.BOSS_SELECTED:
                                self.game.make_beam += 1
                                # Put the make a beam action in here
                                enemy.next_plan = Plan.GOTO_BEAM
                            else:
                                # Put the BOSS and his cargo on their plan here
                                enemy.next_plan = Plan.PATH
                                for j in range(3):
                                    cargo_pos = enemy.cargo.get_at(j)
                                    if cargo_pos != -1:
                                        cargo = self.game.enemy_at(cargo_pos)
                                        cargo.next_plan = Plan.PATH
                                        self.launch_attacker_or_cargo(cargo)
                            self.last_selected_boss = position
                        # if attacker is captured fighter without captor boss => launch as attacker, not cargo
                        elif kind == EntityType.CAPTURED_FIGHTER:
                            enemy.next_plan = Plan.DIVE_AWAY
                        else:
                            enemy.next_plan = Plan.PATH

                        self.launch_attacker_or_cargo(enemy)
                        self.delay_timer = ATTACK_DELAY_TIME
                        # if one of the first two in the slots and it isn't a boss, launch only 1
                        # boss may have cargo later in array
                        if not a_boss:
                            break

    def launch_attacker_or_cargo(self, enemy):
        if enemy.plan == Plan.GRID:
            enemy.plan = Plan.PATH
            if enemy.is_cargo():
                position_index = enemy.get_cargo_boss().position_index
            else:
                position_index = enemy.position_index
                self.select_transforms(enemy)
            enemy.path_index = PATH_LAUNCH + gMirror[position_index]
            # if no transform selected
            if enemy.plan != Plan.BLINK:
                enemy.next_path_point()

            if self.game.sfx_get_num_channels(SOUND_DIVE_ATTACK) > 0:
                self.game.sfx_stop(SOUND_DIVE_ATTACK)
            self.game.sfx_play(SOUND_DIVE_ATTACK)

    def choose_next_boss_idx(self):
        initial_pos = pos = self.last_selected_boss
        while True:
            pos += 1
            if pos > 7:
                pos = 4
            enemy = self.game.enemy_at(pos)
            if enemy.plan == Plan.GRID:
                break
            if pos == initial_pos:
                return -1
        return pos

    def can_make_beam(self, player):
        return self.beam_ready > 1 and \
            self.game.make_beam == BeamState.OFF and \
            player.captured_fighter is None and \
            player.enemies_alive > 5 and \
            player.ships[1].plan != Plan.ALIVE and \
            self.number_of_alive_bosses() > 1

    def number_of_alive_bosses(self) -> int:
        count = 0
        for i in range(4, 8):
            if self.game.enemy_at(i).plan != Plan.DEAD:
                count += 1
        return count

    def select_transforms(self, enemy):
        # TODO transforms can be also generated from butterflies only if there are no more bees
        #  it is hence necessary to keep track of the numbers of bees and butterflies
        stage = self.game.player().stage
        if stage >= 15:
            stage = (stage % 15) + 3
        if stage >= 4 and enemy.kind == EntityType.BEE and not self.game.transform_svc.is_active():
            r = random.choices([True, False], weights=[1, 4], k=1)
            if r[0]:
                # 4 <= stage <= 6:
                kind = EntityType.SCORPION
                if 8 <= stage <= 10:
                    kind = EntityType.BOSCONIAN
                elif 12 <= stage <= 14:
                    kind = EntityType.GALAXIAN
                enemy.blink_transform(kind)
