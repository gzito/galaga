from random import randint

import glm

from galaga_data import *
from pyjam.application import Game, pc2v


# ----------------------------------------------
#
# EnemySpawner
#
# ----------------------------------------------
class EnemySpawner:
    def __init__(self, game):
        # True if a wave is spawning, False if not spawning
        self.spawn_wave = False
        # used to wait 1 second between waves
        self.spawn_timer = 0.0

        # index into g_spawn_kind array
        self.challenge_index = 0

        self.extra_enemy = [0, 0]
        self.extra_enemy_count = [0, 0]
        self.next_position = 0

        # list of spawning enemies that will shoot (max 12 enemies/wave)
        self.enemy_to_arm = [0] * 12
        # walks gEnemyToArm circularly
        self.enemy_to_arm_index = 0

        self.game = game

        # a list of enemy forming a single wave during challenge stage
        # used in Enemy.kill to assign scoring when a full wave is cleared
        self.wave_enemies = []

    def spawn_get_next_extra(self, side, number):
        stage = self.game.player().stage
        wave = self.game.player().attack_wave
        give = 0

        # Maximum 2 extra enemies per wave
        if number < 2:
            # stages < 4, and stage 10 don't get extra enemies
            if stage >= 4 and stage != 10:
                if 4 <= stage <= 8:
                    # 5,5,4,4,4,4,5,5,5,5
                    if number == 0 and (wave == 0 or wave > 2):
                        give = 1
                elif stage == 9:
                    # 6,6,5,5,5,5,5,5,5,5
                    give = 1
                    if wave >= 1 and number != 0:
                        give = 0
                elif stage == 12:
                    # 5,5,5,5,5,5,5,5,5,5
                    if number == 0:
                        give = 1
                elif stage == 13:
                    # 6,6,5,5,6,6,6,6,6,6
                    give = 1
                    if wave == 1 and number != 0:
                        give = 0
                else:
                    # 6,6,6,6,6,6,6,6,6,6
                    give = 1

        # if give = 1 then set an extra enemy insert location, else don't give an extra enemy
        if give:
            self.extra_enemy[side] = randint(self.extra_enemy[side], 3)
        else:
            self.extra_enemy[side] = -1

    def setup_new_stage(self):
        every = 0
        bullets = 0

        player = self.game.player()

        player.grid.reset()

        player.enemies_alive = 0
        player.attack_wave = 0
        player.spawn_index[0] = 0
        player.spawn_index[1] = 0
        player.kind_index = 0

        for et in self.game.ent_svc.ent_data.keys():
            self.game.ent_svc.set_sprites_used(et, Game.instance.current_player_idx, 0)

        stage = player.stage
        if stage < 2:
            player.stage_index = 2
        elif stage == 2:
            player.stage_index = 1
        else:
            player.stage_index = stage & 3

        # Non-challange state extra init
        if self.game.player().stage_index != 3:
            # not a challanging stage
            self.challenge_index = 0

            # Calculate which spawning enemies will fire how many shots
            # stage 0,1 no shooting
            if stage >= 2:
                # stages > 5 every other enemy shoots
                if stage > 5:
                    # except for stage 10 where nobody shoots
                    if stage == 10:
                        every = 0
                    else:
                        every = 2
                else:
                    # 2 - 5, every 3rd enemy shoots
                    every = 3

            if stage <= 4:
                bullets = 1
            else:
                bullets = 2
        else:
            # is a challanging stage
            challaging_stage = 1 + round(((self.game.player().stage - 2) >> 2) % 3)
            # index into gSpawnKind array
            self.challenge_index = 5 * challaging_stage
            # calculate stageIndex for challenge stage
            self.game.player().stage_index = 2 + challaging_stage

        for i in range(len(self.enemy_to_arm)):
            self.enemy_to_arm[i] = 0
            if every:
                if i % every != 0:
                    self.enemy_to_arm[i] = bullets

        self.spawn_timer = 0.15
        self.game.quiescence = False
        self.spawn_wave = False
        player.spawn_active = True

        # Not in player data - only matters in challanging stages where player can't die
        self.game.enemies_killed_this_stage = 0

        # There are 0-39 grid positions and 40-43 are for extra, peel-away enemies
        self.next_position = 44

        # Init the extra enemy management variables
        self.extra_enemy[0] = 0
        self.extra_enemy[1] = 0

        self.extra_enemy_count[0] = 0
        self.extra_enemy_count[1] = 0

        self.spawn_get_next_extra(0, 0)
        self.spawn_get_next_extra(1, 0)

    def setup_new_enemy(self, enemy, position: int):
        wave = 0

        path = [0, 0]
        if position < 44:
            next_plan = Plan.GOTO_GRID
        else:
            next_plan = Plan.DIVE_AWAY_LAUNCH

        # On challange stages, the enemies go straight to death at the end of the path
        if self.challenge_index != 0:
            next_plan = Plan.DEAD
            self.wave_enemies.append(position)

        current_player = self.game.player()

        kind = gSpawn_kind[current_player.attack_wave][current_player.kind_index]
        # path[0] -> left side
        path[0] = gPath_indicies[current_player.stage_index][current_player.attack_wave][0]
        # path[1] -> right side
        path[1] = gPath_indicies[current_player.stage_index][current_player.attack_wave][1]
        the_path = path[current_player.kind_index]

        enemy.kind = kind
        enemy.sprite = self.game.get_first_free_sprite_by_ent_type(kind)
        enemy.position_index = position
        enemy.plan = Plan.PATH
        enemy.next_plan = next_plan
        enemy.path_index = the_path
        enemy.attack_index = -1
        enemy.cargo_index = -1

        # start position of the path
        index = the_path >> 1
        enemy.x = gStartPath[index][0]
        enemy.y = gStartPath[index][1]

        # Mirror if path is odd
        if the_path & 1 != 0:
            enemy.x = 100.0 - gStartPath[index][0]

        # Special case challenging stages
        # challenging stage 3 (stage 11 seen first)
        if self.challenge_index == 15:
            wave = self.game.player().attack_wave
            # if the path is odd on wave 0 and 3 then don't mirror the start
            if the_path & 1:
                if wave == 0 or wave == 3:
                    enemy.x = 100 - enemy.x
            else:
                # but if it's not mirrored on wave 4 then do mirror its start
                if wave == 4:
                    enemy.x = 100 - enemy.x

        enemy.point_index = 0
        enemy.next_path_point()

        enemy.sprite.position = pc2v(glm.vec2(enemy.x, enemy.y))
        enemy.sprite.visible = True

        # setup the firing
        enemy.shots_to_fire = self.enemy_to_arm[self.enemy_to_arm_index]
        if self.enemy_to_arm[self.enemy_to_arm_index]:
            if aPath_Bottom_Single <= index <= aPath_Bottom_Double_In:
                enemy.timer = 1.0 + (randint(0, 3) / 10.0)
            else:
                enemy.timer = 0.3 + (randint(0, 3) / 10.0)
        else:
            enemy.timer = 0
        self.enemy_to_arm_index += 1
        if self.enemy_to_arm_index >= len(self.enemy_to_arm):
            self.enemy_to_arm_index = 0

        # One more enemy to kill
        current_player.enemies_alive += 1

        # wait a small amount between non-side-by-side enemies, and pairs of side-by-side enemies
        if self.spawn_wave and path[0] == path[1] or current_player.kind_index == 1:
            self.spawn_timer = 0.10

        # challenging stage 3 uses seperate paths but delay spawn as thoug it's a single path
        if self.challenge_index == 15:
            if wave == 0 or wave == 3 or wave == 4:
                self.spawn_timer = 0.10

    def run(self):
        self.spawn_timer -= self.game.delta_time

        player = self.game.player()

        if not self.spawn_wave and self.game.quiescence:
            self.wave_enemies.clear()

        # wait 1 second between waves - wave "done" when in grid or destroyed (challenge or all shot out)
        if not self.spawn_wave and not self.game.quiescence:
            if not Game.instance.fast_spawn:
                self.spawn_timer = 1.0
            else:
                self.spawn_timer = 0.0

        if self.spawn_timer <= 0.0:
            self.spawn_wave = True

            # each wave has 2 "sides" or streams
            # each time a new enemy is spawn, change the side (left <-> right)
            side = player.kind_index

            # see if an extra enemy needs to be inserted now
            if player.spawn_index[side] == self.extra_enemy[side]:
                position = self.next_position
                self.next_position += 1
                if self.next_position == 48:
                    self.next_position = 44
                self.extra_enemy_count[side] += 1
                self.spawn_get_next_extra(side, self.extra_enemy_count[side])
            else:
                # where in the grid should this enemy go
                position = gSpawn_order[player.attack_wave][side][player.spawn_index[side]]

            self.setup_new_enemy(self.game.enemy_at(position), position)

            if position < 44:
                player.spawn_index[side] += 1
                if player.spawn_index[side] >= len(gSpawn_order[player.attack_wave][side]):
                    player.spawn_index[side] = 0
                    # if the whole wave has spawned then go to the next wave
                    if side == 1:
                        self.spawn_wave = False
                        player.attack_wave += 1
                        # if all waves have spawned then spawning is done
                        if player.attack_wave >= len(gSpawn_order):
                            player.attack_wave = 0
                            player.spawn_active = False
                        else:
                            # Reset variables per wave
                            self.extra_enemy[0] = 0
                            self.extra_enemy[1] = 0
                            self.extra_enemy_count[0] = 0
                            self.extra_enemy_count[1] = 0

                            self.spawn_get_next_extra(0, 0)
                            self.spawn_get_next_extra(1, 0)

            # Flip between the two sides of the attack wave
            player.kind_index = 1 - player.kind_index
