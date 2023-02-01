from galaga_data import *


class AttackService:
    def __init__(self, game):
        self.__game = game

        # True if it is ready for attack, otherwise False
        self.__bugs_attack = False
        # -1 = empty or # is grid-position
        self.__attackers = [-1, -1]
        # -1 = empty or # is grid-position; item 2 is reserved to captured fighter
        self.__cargo = [-1, -1, -1]
        # max 2 attackers
        self.__num_attackers = 0
        # max 2 cargo (excluded captured fighter)
        self.__num_cargo = 0
        # index into __attackers of a boss making beam, -1 none
        self.__beam_boss_idx = -1
        # index into __attackers of a boss bringing cargo, -1 none
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

    def cargo_count(self):
        return self.__num_cargo

    def attackers_count(self):
        return self.__num_attackers

    @property
    def attackers(self):
        return self.__attackers

    @property
    def cargo(self):
        return self.__cargo

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

    def clear_all(self):
        self.clear_all_attackers()
        self.clear_all_cargo()

    # ------------------------------
    # attackers
    # ------------------------------

    def clear_all_attackers(self):
        """
        clear all attackers slots
        """
        for i in range(len(self.__attackers)):
            self.clear_attacker(i)
        self.__num_attackers = 0

    def get_attacker_at(self, idx):
        return self.__attackers[idx]

    def add_attacker(self, from_idx, position_in_the_grid):
        """
        add an attacker at the first available slot starting from the index from_idx
        """
        for i in range(from_idx, len(self.__attackers)):
            if self.__attackers[i] == -1:
                self.__attackers[i] = position_in_the_grid
                self.__game.enemy_at(position_in_the_grid).attack_index = i
                self.__num_attackers += 1
                break

    def append_attacker(self, position_in_the_grid):
        """
        append an attacker
        """
        self.__attackers[self.__num_attackers] = position_in_the_grid
        self.__game.enemy_at(position_in_the_grid).attack_index = self.__num_attackers
        self.__num_attackers += 1

    def clear_attacker(self, idx):
        """
        clear the attacker at the given slot index
        """
        position = self.__attackers[idx]
        if position != -1:
            enemy = self.__game.enemy_at(position)
            if enemy.is_boss():
                self.beam_boss_idx = -1
                self.cargo_boss_idx = -1
            self.__attackers[idx] = -1
            self.__num_attackers -= 1

    """
    def clear_attacker_by_pos_idx(self, position_in_the_grid):
        # find the cargo with the given position in the grid and delete it from cargo slots #
        for i in range(len(self.__attackers)):
            if self.__attackers[i] == position_in_the_grid:
                self.clear_attacker(i)
                break
    """

    # ------------------------------
    # cargo
    # ------------------------------

    def clear_all_cargo(self):
        for i in range(len(self.__cargo)):
            self.clear_cargo(i)
        self.__num_cargo = 0

    def get_cargo_at(self, idx):
        return self.__cargo[idx]

    def add_cargo(self, from_idx, position_in_the_grid):
        """
        add a cargo at the first available slot starting from the index from_idx
        """
        for i in range(from_idx, len(self.__cargo)):
            if self.__cargo[i] == -1:
                self.__cargo[i] = position_in_the_grid
                self.__game.enemy_at(position_in_the_grid).cargo_index = i
                self.__num_cargo += 1
                break

    def clear_cargo(self, idx):
        """
        delete the cargo with the given index from cargo slots
        """
        if self.__cargo[idx] != -1:
            self.__cargo[idx] = -1
            self.__num_cargo -= 1

    """
    def clear_cargo_by_pos_idx(self, position_in_the_grid):
        # find the cargo with the given position in the grid and delete it from cargo slots #
        for i in range(len(self.__cargo)):
            if self.__cargo[i] == position_in_the_grid:
                self.clear_cargo(i)
                break
    """

    @property
    def delay_timer(self):
        return self.__attack_delay_timer

    def decr_delay_timer(self, delta_time):
        self.__attack_delay_timer -= delta_time

    def set_delay_timer(self, value):
        self.__attack_delay_timer = value

    # try to select al least 2 attackers
    def attack_ready(self) -> bool:
        if self.game.player().spawn_active:
            return False
        if not self.game.quiescence:
            return False

        self.game.make_beam = BeamState.OFF
        self.beam_ready = 0

        # prime the attack structure with 2 attackers, not bosses, hence start looking from position 8
        self.clear_all_attackers()
        for position in gAttack_order:
            if self.attackers_count() < 2:
                if self.game.enemy_at(position).plan == Plan.GRID:
                    self.append_attacker(position)
            else:
                break

        return True

    def choose_attacker(self):
        # while the capture sequence is active, disable attackers
        if self.game.player().capture_state != CaptureState.OFF and self.game.player().capture_state != CaptureState.READY:
            return

        self.decr_delay_timer(self.game.delta_time)

        if self.delay_timer < 0.0:
            # only allow 2 at a time
            if self.attackers_count() < 2:
                # try to pick a boss
                if self.cargo_boss_idx == -1:
                    position = self.choose_next_boss_idx()
                    if position != -1:
                        boss_entity = self.game.enemy_at(position)
                        if boss_entity.plan == Plan.GRID:
                            self.add_attacker(0, position)

                            # See if this boss should go make a beam
                            if self.beam_ready > 1:
                                if self.game.make_beam == BeamState.OFF and \
                                        self.game.player().captured_fighter is None and \
                                        self.game.player().enemies_alive > 5 and \
                                        self.game.player().ships[1].plan != Plan.ALIVE:
                                    self.game.make_beam = BeamState.BOSS_SELECTED
                                    self.beam_boss_idx = boss_entity.attack_index
                                    self.beam_ready = 0
                            else:
                                self.clear_all_cargo()
                                # See if there's cargo to take and set those ships up on a launch plan as well
                                # if this boss is a captor => there should be a captured fighter in the grid
                                if boss_entity.is_captor():
                                    pos_idx = self.game.player().captured_fighter.position_index
                                    self.add_cargo(2, pos_idx)
                                    self.cargo_boss_idx = boss_entity.attack_index

                                loaded = 0
                                for i in range(3):
                                    pos_idx = position + 5 + i
                                    if self.game.enemy_at(pos_idx).plan == Plan.GRID:
                                        loaded += 1
                                        self.add_cargo(0, pos_idx)
                                        self.cargo_boss_idx = boss_entity.attack_index
                                    if loaded == 2:
                                        break

                                self.beam_ready += 1

            # after boss pick, if still a slot, try to pick a bee or butterfly
            if self.cargo_boss_idx == -1:
                if self.attackers_count() < 2:
                    for position in gAttack_order:
                        # if idle
                        if self.game.enemy_at(position).plan == Plan.GRID:
                            self.add_attacker(0, position)
                            # Exit loop as an enemy was put in a slot
                            break

                # if there is the captured fighter without its captor boss
                if self.game.player().captured_fighter is not None and self.game.player().get_captor_boss() is None:
                    # if still a free slot, select it as an attacker
                    if self.attackers_count() < 2:
                        position = self.game.player().captured_fighter.position_index
                        if self.game.player().captured_fighter.plan == Plan.GRID:
                            self.add_attacker(0, position)

            # launch any attackers that haven't launched yet
            # This is done as a second part so that the initial primed 2 non-boss
            # attackers will get launched in this way
            for i in range(len(self.attackers)):
                position = self.get_attacker_at(i)
                if position != -1:
                    # is this enemy idle or has it launched ?
                    enemy = self.game.enemy_at(position)
                    if enemy.plan == Plan.GRID:
                        # Make it launch if it was still idle
                        kind = enemy.kind
                        a_boss = (kind == EntityType.BOSS_GREEN) or (kind == EntityType.BOSS_BLUE)
                        # if attacker is a boss
                        if a_boss:
                            if self.game.make_beam == BeamState.BOSS_SELECTED:
                                self.game.make_beam += 1
                                # Put the make a beam action in here
                                enemy.next_plan = Plan.GOTO_BEAM
                            else:
                                # Put the BOSS and his cargo on their plan here
                                enemy.next_plan = Plan.PATH
                                for j in range(len(self.cargo)):
                                    cargo_pos = self.get_cargo_at(j)
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
                        self.set_delay_timer(ATTACK_DELAY_TIME)
                        # if one of the first two in the slots and it isn't a boss, launch only 1
                        # boss may have cargo later in array
                        if not a_boss:
                            break

    def launch_attacker_or_cargo(self, enemy):
        if enemy.plan == Plan.GRID:
            enemy.plan = Plan.PATH
            enemy.path_index = PATH_LAUNCH + gMirror[enemy.position_index]
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
