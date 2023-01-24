import copy

import glm

from spawn import EnemySpawner
from galaga_data import *
from pyjam.application import GameState, pc2v, vx2pcx, pcx2vx, vy2pcy, pcy2vy


class Attackers:
    def __init__(self):
        # -1 = empty or # is grid-position
        self.__attackers = [-1, -1, -1, -1]
        self.__num_attackers = 0
        self.__attack_delay_timer = 0.0

    @property
    def count(self):
        return self.__num_attackers

    def get_at(self, idx):
        return self.__attackers[idx]

    @property
    def delay_timer(self):
        return self.__attack_delay_timer

    def decr_delay_timer(self, delta_time):
        self.__attack_delay_timer -= delta_time

    def set_delay_timer(self, value):
        self.__attack_delay_timer = value

    def clear_all(self):
        for i in range(len(self.__attackers)):
            self.__attackers[i] = -1
        self.__num_attackers = 0

    def add_attacker(self, from_idx, position):
        for i in range(from_idx, len(self.__attackers)):
            if self.__attackers[i] == -1:
                self.set_attacker_at(i, position)
                break

    def set_attacker(self, position):
        self.__attackers[self.__num_attackers] = position
        self.__num_attackers += 1

    def set_attacker_at(self, idx, position):
        self.__attackers[idx] = position
        self.__num_attackers += 1

    def clear_attacker(self, idx):
        self.__attackers[idx] = -1
        self.__num_attackers -= 1



# ===================================================================================================
# PlayingState
# ===================================================================================================
class PlayingState(GameState):
    class Substate(IntEnum):
        InitGame = 1,
        StageInit = 2,
        StageIconsInit = 3,
        PreShowField = 4,
        StageIcons = 5,
        PlayerInit = 6,
        PrePlay = 7,
        Play = 8,
        StageClear = 9,
        PlayerDied = 10,
        HideField = 11,
        NextToPlay = 12,
        ShowField = 13,
        ShowChallengeResults = 14,
        PlayerGameOver = 15,
        ShowGameOverStats = 16,
        HoldGameOverStats = 17,
        HighScore = 18,
        HoldHighScore = 19

    def __init__(self, game, substate):
        super().__init__(game)

        self.__state_timer = 0.0
        self.__spawner = None
        self.__substate = substate
        self.__scratch1 = 0
        self.__scratch2 = 0
        self.__game_over = False
        self.__attackers = Attackers()
        self.__bugs_attack = False

    @property
    def substate(self):
        return self.__substate

    @substate.setter
    def substate(self, new_state):
        self.__substate = new_state
        self.__scratch1 = 0
        self.__scratch2 = 0
        self.__state_timer = 0.0

    @property
    def spawner(self):
        return self.__spawner

    @property
    def bugs_attack(self) -> bool:
        return self.__bugs_attack

    @property
    def attackers(self):
        return self.__attackers

    def is_game_over(self):
        return self.__game_over

    def enter(self):
        self.__spawner = EnemySpawner(self.game)

    def update(self):
        self.handle_player()
        self.move_bullets()
        self.update_enemies()
        self.game.fx_svc.update(self.game.delta_time)

        self.__state_timer -= self.game.delta_time

        # InitGame
        if self.substate == PlayingState.Substate.InitGame:
            self.setup_player(0)
            self.setup_player(1)
            self.game.current_player_idx = 0
            self.game.stars_svc.speed = 0
            self.game.make_beam = BeamState.OFF
            self.game.sfx_play(SOUND_START)
            self.game.set_text_range_visible(TEXT_2UP, TEXT_SCORE2P, self.game.num_players > 1)
            self.game.texts[TEXT_PLAYER_NUM].text = '1'
            self.game.texts[TEXT_PLAYER].position = pc2v(glm.vec2(39, 50))
            self.game.texts[TEXT_PLAYER_NUM].position = pc2v(glm.vec2(65, 50))
            self.game.set_text_range_visible(TEXT_PLAYER, TEXT_PLAYER_NUM, True)
            self.substate = PlayingState.Substate.StageInit
            self.__state_timer = 4.0
        # StageInit
        elif self.substate == PlayingState.Substate.StageInit:
            if self.__state_timer < 0:
                self.__spawner.setup_new_stage()
                print(f'self.game.player().stage = {self.game.player().stage}')
                print(f'self.game.player().stage_index = {self.game.player().stage_index}')
                self.game.bullet_index = self.game.ent_svc.get_sprite_numbers(EntityType.BLUE_BULLET)
                self.game.set_text_range_visible(TEXT_PLAYER, TEXT_PLAYER_NUM, False)
                if self.game.player().stage_index < 3:
                    self.game.texts[TEXT_STAGE_NUM].text = str(self.game.player().stage)
                    self.game.set_text_range_visible(TEXT_STAGE, TEXT_STAGE_NUM, True)
                else:
                    self.game.texts[TEXT_CHALLENGING_STAGE].visible = True
                    self.game.sfx_play(SOUND_CHALLENGE_STAGE)
                self.game.set_text_range_visible(TEXT_CREDIT, TEXT_0, False)
                self.setup_stage_icons(self.game.player().stage_icons_to_show)
                self.game.player().stage_icons_shown.clear()
                self.game.bug_attack_speed = \
                    BUG_ATTACK_SPEED_BASE + \
                    ((BUG_ATTACK_SPEED_MAX - BUG_ATTACK_SPEED_BASE) / BUG_ATTACK_SPEED_WINDOW) * \
                    (self.game.player().stage % BUG_ATTACK_SPEED_WINDOW)
                self.substate = PlayingState.Substate.PreShowField
        # PreShowField
        elif self.substate == PlayingState.Substate.PreShowField:
            self.show_lives_icons()

            self.game.set_sprite_range_visible(self.game.ent_svc.get_sprite_offset(EntityType.BADGE1),
                                               self.game.ent_svc.get_last_sprite_idx(EntityType.BADGE50),
                                               False)

            for sprite in self.game.player().stage_icons_shown:
                sprite.visible = True

            self.substate = PlayingState.Substate.ShowField
        # ShowField
        elif self.substate == PlayingState.Substate.ShowField:
            if self.game.player().grid.y_offset < 0:
                self.game.player().grid.y_offset += LEAVE_GRID_SPEED * self.game.delta_time
            else:
                self.game.player().grid.y_offset = 0
                self.substate = PlayingState.Substate.StageIcons
        # StageIcons
        elif self.substate == PlayingState.Substate.StageIcons:
            if len(self.game.player().stage_icons_to_show) > 0:
                if self.__state_timer <= 0:
                    if self.game.player().stage > 1:
                        self.game.sfx_play(SOUND_STAGE_ICON)
                    sprite = self.game.player().stage_icons_to_show.pop()
                    sprite.visible = True
                    self.game.player().stage_icons_shown.append(sprite)
                    if len(self.game.player().stage_icons_to_show) > 0:
                        self.__state_timer = TIME_TO_NEXT_STAGE_ICON
            else:
                self.substate = PlayingState.Substate.PlayerInit
                self.__state_timer = 1.5
        # PlayerInit
        elif self.substate == PlayingState.Substate.PlayerInit:
            if self.__state_timer < 0:
                if self.game.player().ships[0].plan < Plan.ALIVE:
                    self.game.player().ships[0].x = 50
                    self.game.player().ships[0].sprite.position = \
                        pc2v(glm.vec2(self.game.player().ships[0].x,
                                      self.game.player().ships[0].y))

                if self.game.num_players > 1 or self.game.player().ships[0].plan == Plan.INIT:
                    # Show PLAYER 1 label
                    self.game.texts[TEXT_PLAYER_NUM].text = str(self.game.current_player_idx + 1)
                    self.game.texts[TEXT_PLAYER].position = pc2v(glm.vec2(36.0, 44.5))
                    self.game.texts[TEXT_PLAYER_NUM].position = pc2v(glm.vec2(61.5, 44.5))
                    self.game.set_text_range_visible(TEXT_PLAYER, TEXT_PLAYER_NUM, True)

                self.game.player().ships[0].plan = Plan.ALIVE
                self.game.player().ships[0].sprite.visible = True
                self.substate = PlayingState.Substate.PrePlay
                self.__state_timer = 1.5
        # PrePlay
        elif self.substate == PlayingState.Substate.PrePlay:
            if self.game.stars_svc.speed < STAR_MAX_SPEED:
                self.game.stars_svc.speed += self.game.delta_time * STAR_ACCELERATION
            if self.__state_timer < 0:
                self.game.set_text_range_visible(TEXT_PLAYER, TEXT_READY, False)
                self.game.stars_svc.speed = STAR_MAX_SPEED
                self.substate = PlayingState.Substate.Play
                self.__bugs_attack = False
                self.attackers.clear_all()
        # Play
        elif self.substate == PlayingState.Substate.Play:
            # Test for end of stage - all clear - condition
            # do before testing if player has died as that needs to go to a different state
            if self.game.player().enemies_alive == 0 and not self.game.player().spawn_active and \
                    self.game.player().capture_state == CaptureState.OFF:
                self.game.sfx_stop(SOUND_BREATHING_TIME)
                self.game.player().stage += 1
                if self.game.player().stage == 256:
                    self.game.player().stage = 0
                self.substate = PlayingState.Substate.StageClear

            if self.game.player().ships[0].plan != Plan.DEAD:
                if self.game.player().spawn_active:
                    self.__spawner.run()
                if not self.__bugs_attack:
                    self.__bugs_attack = self.attack_ready()
                if self.__bugs_attack:
                    self.choose_attacker()
            elif self.game.player().ships[1].plan != Plan.ALIVE:
                self.substate = PlayingState.Substate.PlayerDied
        # StageClear
        elif self.substate == PlayingState.Substate.StageClear:
            if len(self.game.fx_svc.effects) == 0:
                if self.game.player().stage_index >= 3:
                    if self.game.enemies_killed_this_stage == 40:
                        self.game.sfx_play(SOUND_CHALLENGE_PERFECT)
                    else:
                        self.game.sfx_play(SOUND_CHALLENGE_BONUS)
                    self.substate = PlayingState.Substate.ShowChallengeResults
                    self.__state_timer = 2.0
                else:
                    self.substate = PlayingState.Substate.StageInit
        # PlayerDied
        elif self.substate == PlayingState.Substate.PlayerDied:
            if not self.game.quiescence or len(self.game.fx_svc.effects) != 0:
                if self.__spawner.spawn_wave:
                    self.__spawner.run()
            else:
                if not self.game.infinite_lives:
                    self.game.player().lives -= 1
                if self.game.player().lives < 0:
                    self.substate = PlayingState.Substate.PlayerGameOver
                else:
                    if self.game.num_players > 1 and self.game.player().enemies_alive:
                        self.substate = PlayingState.Substate.HideField
                    else:
                        self.substate = PlayingState.Substate.NextToPlay
        # HideField
        elif self.substate == PlayingState.Substate.HideField:
            if self.game.player().grid.y_offset > -50:
                self.game.player().grid.y_offset -= LEAVE_GRID_SPEED * self.game.delta_time
            else:
                for i in range(MAX_ENEMIES):
                    if self.game.enemy_at(i).plan:
                        self.game.enemy_at(i).sprite.visible = False
                self.substate = PlayingState.Substate.NextToPlay
        # NextToPlay
        elif self.substate == PlayingState.Substate.NextToPlay:
            # Turn on the 1UP/2UP indicator
            index = self.game.texts[self.game.flash_index[self.game.current_player_idx]]
            index.visible = True

            # Switch players if needed
            if self.game.num_players > 1:
                next_player = 1 - self.game.current_player_idx
                if self.game.players[next_player].lives >= 0:
                    self.game.current_player_idx = next_player

            # if switching to a lifeless player, all players are dead
            if self.game.player().lives < 0:
                self.game.stars_svc.speed = STAR_MAX_SPEED
                self.__game_over = True
                return

            # Put the sprites in the right spots for this player and make them visible
            if self.game.num_players > 1:
                for i in range(MAX_ENEMIES):
                    enemy = self.game.enemy_at(i)
                    if enemy.plan:
                        enemy.sprite.x = pcx2vx(enemy.x)
                        enemy.sprite.y = pcy2vy(enemy.y)
                        enemy.sprite.visible = True

            # continue the stage or start a new stage if all enemies were killed
            if self.game.player().enemies_alive or self.game.player().spawn_active:
                self.game.texts[TEXT_READY].visible = True
                self.substate = PlayingState.Substate.PreShowField
            else:
                self.substate = PlayingState.Substate.StageInit
        # ShowChallengeResults
        elif self.substate == PlayingState.Substate.ShowChallengeResults:
            # Show enemies killed and award a bonus after challange stage
            if self.__state_timer < 0:
                if self.__scratch1 == 0:
                    self.game.texts[TEXT_NUMBER_OF_HITS].color = COLOR_ROBIN
                    self.game.texts[TEXT_NUMBER_OF_HITS].position = pc2v(glm.vec2(18, 50.0))
                    self.game.texts[TEXT_NUMBER_OF_HITS].visible = True
                    self.__state_timer = 1.0
                    self.__scratch1 += 1
                elif self.__scratch1 == 1:
                    self.game.texts[TEXT_NUMBER_OF_HITS_NUM].color = COLOR_ROBIN
                    self.game.texts[TEXT_NUMBER_OF_HITS_NUM].position = pc2v(glm.vec2(75, 50.0))
                    self.game.texts[TEXT_NUMBER_OF_HITS_NUM].text = str(self.game.enemies_killed_this_stage)
                    self.game.texts[TEXT_NUMBER_OF_HITS_NUM].visible = True
                    self.__state_timer = 1.0
                    self.__scratch1 += 1
                elif self.__scratch1 == 2:
                    if self.game.enemies_killed_this_stage == 40:
                        self.game.texts[TEXT_PERFECT].visible = not self.game.texts[TEXT_PERFECT].visible
                        self.__scratch2 += 1
                        if self.__scratch2 > 6:
                            self.__scratch1 += 1
                        self.__state_timer = 0.25
                    else:
                        self.game.texts[TEXT_BONUS].visible = True
                        self.__state_timer = 1.0
                        self.__scratch1 += 1
                elif self.__scratch1 == 3:
                    if self.game.enemies_killed_this_stage == 40:
                        self.game.texts[TEXT_SPECIAL_BONUS].visible = True
                        self.game.increment_score(10000)
                    else:
                        score_amount = self.game.enemies_killed_this_stage * 100
                        self.game.texts[TEXT_BONUS_NUM].text = str(score_amount)
                        self.game.texts[TEXT_BONUS_NUM].visible = True
                        self.game.increment_score(score_amount)
                    self.__state_timer = 4.0
                    self.__scratch1 += 1
                elif self.__scratch1 == 4:
                    self.game.set_text_range_visible(TEXT_NUMBER_OF_HITS, TEXT_PERFECT, False)
                    self.substate = PlayingState.Substate.StageInit
        # PlayerGameOver
        elif self.substate == PlayingState.Substate.PlayerGameOver:
            self.game.player().ships[0].sprite.visible = False
            self.game.player().ships[1].sprite.visible = False
            if self.game.num_players > 1:
                self.game.texts[TEXT_PLAYER].position = pc2v(glm.vec2(39.5, 44.0))
                self.game.texts[TEXT_PLAYER_NUM].position = pc2v(glm.vec2(65.0, 44.0))
                self.game.set_text_range_visible(TEXT_PLAYER, TEXT_PLAYER_NUM, True)
            self.game.texts[TEXT_GAME_OVER].visible = True
            self.substate = PlayingState.Substate.ShowGameOverStats
            self.__state_timer = 3.0
        # ShowGameOverStats
        elif self.substate == PlayingState.Substate.ShowGameOverStats:
            if self.__state_timer < 0.0:
                self.game.set_sprite_range_visible(self.game.ent_svc.get_sprite_offset(EntityType.CAPTURED_FIGHTER),
                                                   self.game.ent_svc.get_sprite_offset(EntityType.RED_BULLET), False)
                self.game.set_text_range_visible(TEXT_PLAYER, TEXT_PLAYER_NUM, False)
                self.game.texts[TEXT_GAME_OVER].visible = False
                # Update stats text
                self.game.texts[TEXT_SHOTS_FIRED_NUM].text = str(self.game.player().shots_fired)
                self.game.texts[TEXT_NUMBER_OF_HITS_NUM].text = str(self.game.player().hits)
                if self.game.player().shots_fired:
                    hit_miss_ratio_str = '{:.1f} %'.format(
                        (self.game.player().hits * 100.0) / self.game.player().shots_fired)
                else:
                    hit_miss_ratio_str = g_texts_data[TEXT_HIT_MISS_RATIO_NUM][1]
                self.game.texts[TEXT_HIT_MISS_RATIO_NUM].text = hit_miss_ratio_str
                # show stats
                self.game.texts[TEXT_NUMBER_OF_HITS].color = COLOR_YELLOW
                self.game.texts[TEXT_NUMBER_OF_HITS].position = pc2v(glm.vec2(14.5, 64.0))
                self.game.texts[TEXT_NUMBER_OF_HITS_NUM].color = COLOR_YELLOW
                self.game.texts[TEXT_NUMBER_OF_HITS_NUM].position = pc2v(glm.vec2(72.0, 64.0))
                self.game.set_text_range_visible(TEXT_RESULTS, TEXT_NUMBER_OF_HITS_NUM, True)
                self.substate = PlayingState.Substate.HoldGameOverStats
                self.__state_timer = 7.3
        # HoldGameOverStats
        elif self.substate == PlayingState.Substate.HoldGameOverStats:
            if self.__state_timer < 0.0:
                self.game.sfx_stop(SOUND_BREATHING_TIME)

                self.game.set_text_range_visible(TEXT_RESULTS, TEXT_NUMBER_OF_HITS_NUM, False)
                # if high score - go to enter high score
                lb = self.game.leaderboard
                if self.game.player().score > lb.high_scores[-1].score:
                    lb.edit_score = len(lb.high_scores) - 2
                    lb.edit_letter = 0
                    lb.entry.name = 'AAA'
                    lb.entry.score = self.game.player().score

                    while lb.edit_score >= 0:
                        # Move old scores to make room for new entry
                        if lb.entry.score > lb.high_scores[lb.edit_score].score:
                            self.game.texts[TEXT_SCORE_1 + lb.edit_score + 1].text =\
                                self.game.texts[TEXT_SCORE_1 + lb.edit_score].text
                            self.game.texts[TEXT_N_N + lb.edit_score + 1].text =\
                                self.game.texts[TEXT_N_N + lb.edit_score].text
                            lb.edit_score -= 1
                        else:
                            break
                    lb.edit_score += 1
                    # Add the new entry in where it belongs
                    lb.high_scores.insert(lb.edit_score, copy.copy(lb.entry))
                    # remove the score that's fallen off the bottom
                    lb.high_scores.pop()
                    # Setup to get initials
                    self.game.texts[TEXT_INITALS_SCORE_NUM].text = self.game.format_score(lb.entry.score)
                    self.game.texts[TEXT_SCORE_1 + lb.edit_score].text = self.game.format_score(lb.entry.score)
                    self.game.texts[TEXT_INITALS_INITIALS].text = lb.entry.name
                    self.game.texts[TEXT_N_N + lb.edit_score].text = '   '
                    self.game.texts[TEXT_1ST + lb.edit_score].color = COLOR_YELLOW
                    self.game.texts[TEXT_SCORE_1 + lb.edit_score].color = COLOR_YELLOW
                    self.game.texts[TEXT_N_N + lb.edit_score].color = COLOR_YELLOW
                    self.game.set_text_range_visible(TEXT_SCORE, TEXT_TOP_5, True)
                    self.game.sfx_play(SOUND_HIGHSCORE_LOOP)
                    self.substate = PlayingState.Substate.HighScore
                else:
                    self.substate = PlayingState.Substate.NextToPlay
        # HighScore
        elif self.substate == PlayingState.Substate.HighScore:
            if not self.game.sfx_get_num_channels(SOUND_HIGHSCORE_LOOP):
                self.game.sfx_play(SOUND_HIGHSCORE_LOOP)

            lb = self.game.leaderboard
            if self.__state_timer <= 0.0:
                if self.game.texts[TEXT_INITALS_INITIALS].get_char_color(lb.edit_letter) == COLOR_YELLOW:
                    self.game.texts[TEXT_INITALS_INITIALS].set_char_color(lb.edit_letter, COLOR_ROBIN)
                else:
                    self.game.texts[TEXT_INITALS_INITIALS].set_char_color(lb.edit_letter, COLOR_YELLOW)
                self.__state_timer = 0.25

            # Use debounced directions
            if self.game.managed_dir != 0:
                # Only some alphabet available for initials
                letter = ord(lb.entry.name[lb.edit_letter])
                if self.game.managed_dir == -1:
                    if letter == ord('A'):
                        letter = ord('.')
                    elif letter == ord('.'):
                        letter = ord(' ')
                    elif letter == ord(' '):
                        letter = ord('Z')
                    else:
                        letter -= 1
                else:
                    if letter == ord('Z'):
                        letter = ord(' ')
                    elif letter == ord(' '):
                        letter = ord('.')
                    elif letter == ord('.'):
                        letter = ord('A')
                    else:
                        letter += 1

                lb.entry.name = lb.entry.name[0:lb.edit_letter] + chr(letter) + lb.entry.name[lb.edit_letter+1:]
                self.game.texts[TEXT_INITALS_INITIALS].text = lb.entry.name

            # On fire, lock in an initial - 3 locked in ends the sequence
            if self.game.fire:
                self.game.texts[TEXT_INITALS_INITIALS].set_char_color(lb.edit_letter, COLOR_RED)
                self.game.texts[TEXT_N_N + lb.edit_score].text = lb.entry.name[0:lb.edit_letter+1]
                lb.edit_letter += 1
                if lb.edit_letter > 2:
                    lb.high_scores[lb.edit_score].name = lb.entry.name
                    lb.save()
                    self.substate = PlayingState.Substate.HoldHighScore
                    self.__state_timer = 4.0
        # HoldHighScore
        elif self.substate == PlayingState.Substate.HoldHighScore:
            if self.__state_timer < 0.0:
                # wait for the tune to finish
                if not self.game.sfx_get_num_channels(SOUND_HIGHSCORE_LOOP):
                    if not self.__scratch1:
                        # play the end of tune sound
                        self.game.sfx_play(SOUND_HIGHSCORE_END)
                        self.__scratch1 += 1
                        # wait for end of tune to finish before finally taking the screen down
                    elif not self.game.sfx_get_num_channels(SOUND_HIGHSCORE_END):
                        lb = self.game.leaderboard
                        # Set the color for the new entry back to robin (from the highlighted yellow)
                        self.game.texts[TEXT_1ST + lb.edit_score].color = COLOR_ROBIN
                        self.game.texts[TEXT_SCORE_1 + lb.edit_score].color = COLOR_ROBIN
                        self.game.texts[TEXT_N_N + lb.edit_score].color = COLOR_ROBIN
                        # Hide all the high-score text
                        self.game.set_text_range_visible(TEXT_SCORE, TEXT_TOP_5, False)
                        self.substate = PlayingState.Substate.NextToPlay
            else:
                if not self.game.sfx_get_num_channels(SOUND_HIGHSCORE_LOOP):
                    self.game.sfx_play(SOUND_HIGHSCORE_LOOP)

    def setup_player(self, player_num: int):
        player = self.game.players[player_num]
        p_sprite_offset = self.game.ent_svc.get_sprite_offset(EntityType.FIGHTER)

        player.ships[0].x = 50
        player.ships[0].y = ((ORIGINAL_Y_CELLSF - 3.0) / ORIGINAL_Y_CELLSF) * 100

        player.ships[1].x = 50 + pcx2vx(self.game.sprites[p_sprite_offset].width)
        player.ships[1].y = ((ORIGINAL_Y_CELLSF - 3.0) / ORIGINAL_Y_CELLSF) * 100

        player.ships[0].plan = Plan.INIT
        player.ships[1].plan = Plan.INIT

        player.ships[0].sprite = self.game.sprites[p_sprite_offset]
        player.ships[1].sprite = self.game.sprites[p_sprite_offset + 1]
        player.ships[0].sprite.position = pc2v(glm.vec2(player.ships[0].x, player.ships[0].y))
        player.ships[1].sprite.position = pc2v(glm.vec2(player.ships[1].x, player.ships[1].y))

        player.score = 0
        player.lives = 2
        player.stage = 1
        player.enemies_alive = 0
        player.shots_fired = 0
        player.hits = 0

        player.clear_captor_boss()
        player.captured_fighter = None
        player.capture_state = CaptureState.OFF

        self.game.texts[self.game.score_index[player_num]].text = "     00"

        # Set the # of lives sprites to be in a row at the bottom
        p = 1.0
        ypos = ((ORIGINAL_Y_CELLSF - 2) / ORIGINAL_Y_CELLSF) * 100.0
        for i in range(2, self.game.ent_svc.get_sprite_numbers(EntityType.FIGHTER)):
            sprite = self.game.sprites[p_sprite_offset + i]
            sprite.scale = glm.vec2(0.85, 0.85)
            hx = sprite.hotspot.x
            hy = sprite.hotspot.y
            sprite.position.x = pcx2vx(p) + hx
            sprite.position.y = pcy2vy(ypos) + hy
            p += vx2pcx(sprite.width * sprite.scale.x)

        # scale badge icons
        for i in range(self.game.ent_svc.get_sprite_offset(EntityType.BADGE1),
                       self.game.ent_svc.get_sprite_offset(EntityType.BADGE50) +
                       self.game.ent_svc.get_sprite_numbers(EntityType.BADGE50)):
            self.game.sprites[i].scale = glm.vec2(0.85, 0.85)

        # Make sure all bullets are dead
        for bullet in self.game.bullets:
            bullet.plan = Plan.DEAD

        # Make sure all enemies are dead from last game
        for enemy in self.game.enemies[player_num]:
            enemy.plan = Plan.DEAD
            enemy.set_captor(False)

    def handle_player(self):
        self.game.flash_timer += self.game.delta_time
        if self.game.flash_timer >= FLASH_TIME:
            index = self.game.flash_index[self.game.current_player_idx]
            self.game.texts[index].visible = not self.game.texts[index].visible
            self.game.flash_timer = 0.0

        capture_state = self.game.player().capture_state

        if capture_state != CaptureState.OFF:
            self.game.player().handle_capture()

        if self.game.player().is_capturing() or capture_state >= CaptureState.RESCUED:
            return

        if not self.game.player().ships[0].sprite or not self.game.player().ships[0].sprite.visible:
            return

        if self.game.direction:
            if self.game.player().ships[0].plan & Plan.ALIVE:
                newx = self.game.player().ships[0].x
                if self.game.player().ships[1].plan & Plan.ALIVE:
                    # player frame has an empty column of pixels on the right
                    # (it should be 15 px as width, instead is 16)
                    width = vx2pcx(self.game.player().ships[1].sprite.width - 1)
                else:
                    width = 0
                newx += self.game.direction * PLAYER_MOVEMENT_SPEED * self.game.delta_time
                offset_x = vx2pcx(self.game.player().ships[0].sprite.hotspot.x)
                if newx - offset_x < 0:
                    newx = offset_x
                elif newx + offset_x >= 100 - width:
                    newx = 100 - width - offset_x

                self.game.player().ships[0].x = newx
                self.game.player().ships[0].sprite.x = pcx2vx(newx)

                if self.game.player().ships[1].plan == Plan.ALIVE:
                    self.game.player().ships[1].x = newx + width
                    self.game.player().ships[1].sprite.x = pcx2vx(self.game.player().ships[1].x)

        # don't allow firing before play starts
        if self.substate < PlayingState.Substate.Play:
            return

        # don't allow firing during capture sequence
        if capture_state != CaptureState.OFF and capture_state != CaptureState.READY:
            return

        # Fire if not 2 bullets/ship onscreen already
        if self.game.fire:
            if not self.game.bullets[0].plan:
                b_point_index = 0
            elif not self.game.bullets[1].plan:
                b_point_index = 1
            else:
                b_point_index = -1

            if b_point_index >= 0:
                self.game.player().shots_fired += 1
                self.game.sfx_play(SOUND_PLAYER_SHOOT)
                sprite = self.game.bullets[b_point_index].sprite
                self.game.bullets[b_point_index].plan = Plan.ALIVE
                self.game.bullets[b_point_index].x = self.game.player().ships[0].x
                self.game.bullets[b_point_index].y = self.game.player().ships[0].y
                sprite.position = pc2v(glm.vec2(self.game.bullets[b_point_index].x,
                                                self.game.bullets[b_point_index].y))
                sprite.visible = True

                if self.game.player().ships[1].plan == Plan.ALIVE and not self.game.player().is_captured():
                    self.game.player().shots_fired += 1
                    b_point_index += 2
                    sprite = self.game.bullets[b_point_index].sprite
                    self.game.bullets[b_point_index].plan = Plan.ALIVE
                    # player frame has an empty column of pixels on the right
                    # (it should be 15 px as width, instead is 16)
                    self.game.bullets[b_point_index].x = \
                        self.game.bullets[b_point_index - 2].x + vx2pcx(self.game.player().ships[0].sprite.size.x - 1)
                    self.game.bullets[b_point_index].y = self.game.bullets[b_point_index - 2].y
                    sprite.position = pc2v(glm.vec2(self.game.bullets[b_point_index].x,
                                                    self.game.bullets[b_point_index].y))
                    sprite.visible = True

    def move_bullets(self):
        for bullet in self.game.bullets:
            if bullet.plan == Plan.ALIVE:
                sprite = bullet.sprite
                if bullet.entity_type == EntityType.BLUE_BULLET:
                    # TODO: Player bullets only travel in astraight line but
                    #   when the player is being beamed, the bullets can go at an
                    #   angle - add support for that
                    bullet.y -= BULLET_SPEED * self.game.delta_time
                    if bullet.y < (1 / ORIGINAL_Y_CELLSF) * 100:
                        bullet.plan = Plan.DEAD
                        sprite.visible = False
                else:
                    tx = self.game.delta_time * bullet.velocity.x
                    ty = self.game.delta_time * bullet.velocity.y

                    # update the position
                    bullet.x -= tx
                    bullet.y -= ty

                    if bullet.y > ((ORIGINAL_Y_CELLSF - 2) / ORIGINAL_Y_CELLSF) * 100.0:
                        bullet.plan = Plan.DEAD
                        bullet.sprite.visible = False
                    else:
                        if self.game.player().was_hit(sprite):
                            bullet.plan = Plan.DEAD
                            sprite.visible = False

                sprite.position = pc2v(glm.vec2(bullet.x, bullet.y))

    def update_enemies(self):
        if PlayingState.Substate.PlayerInit <= self.__substate <= PlayingState.Substate.ShowField:
            self.game.player().grid.update(self.game.delta_time)

        # assumes the enemies are all standing in the grid
        self.game.quiescence = True

        for enemy in self.game.enemies[self.game.current_player_idx]:
            # if not dead, the enemy must be updated
            if enemy is not None and enemy.plan:
                enemy.update(self.game.delta_time)
                enemy.was_hit()

    def show_lives_icons(self):
        self.game.set_sprite_range_visible(self.game.ent_svc.get_sprite_offset(EntityType.FIGHTER) + 2,
                                           self.game.ent_svc.get_sprite_offset(EntityType.FIGHTER) + 2 +
                                           self.game.player().lives - 1,
                                           True)
        self.game.set_sprite_range_visible(self.game.ent_svc.get_sprite_offset(EntityType.FIGHTER) + 2 +
                                           self.game.player().lives,
                                           self.game.ent_svc.get_last_sprite_idx(EntityType.FIGHTER),
                                           False)

    def setup_stage_icons(self, icons):
        badges = [50, 30, 20, 10, 5, 1]
        counts = [0, 0, 0, 0, 0, 0]

        stage = self.game.player().stage
        for i in range(len(badges)):
            counts[i] = stage // badges[i]
            stage -= counts[i] * badges[i]

        self.game.set_sprite_range_visible(self.game.ent_svc.get_sprite_offset(EntityType.BADGE1),
                                           self.game.ent_svc.get_last_sprite_idx(EntityType.BADGE50),
                                           False)

        x = 99.0
        for i in reversed(range(len(counts))):
            num = counts[i]
            for j in range(num):
                sprite = self.game.get_sprite_at_by_ent_type(EntityType(EntityType.BADGE50 - i), j)
                x -= vx2pcx(sprite.width)
                sprite.position = pc2v(glm.vec2(x, 100.0 - vy2pcy(sprite.height)))
                sprite.hotspot = glm.vec2(0, 0)
                icons.append(sprite)

    # try to select al least 2 attackers
    def attack_ready(self) -> bool:
        if self.game.player().spawn_active:
            return False
        if not self.game.quiescence:
            return False

        # prime the attack structure with 2 attackers, not bosses, hence start looking from 4
        self.attackers.clear_all()
        for position in gAttack_order:
            if self.attackers.count < 2:
                if self.game.enemy_at(position).plan == Plan.GRID:
                    self.attackers.set_attacker(position)
            else:
                break

        return True

    def choose_attacker(self):
        # while the capture sequence is active, disable attackers
        if self.game.player().capture_state != CaptureState.OFF and self.game.player().capture_state != CaptureState.READY:
            return

        self.attackers.decr_delay_timer(self.game.delta_time)

        if self.attackers.delay_timer < 0.0:
            # only allow 2 at a time
            if self.attackers.count < 2:
                # try to pick a boss
                for position in range(4, 8):
                    if self.game.enemy_at(position).plan == Plan.GRID:
                        self.attackers.add_attacker(0, position)

                        # See if this boss should go make a beam
                        if self.game.make_beam == BeamState.OFF and self.game.player().captured_fighter is None:
                            if self.game.player().enemies_alive > 5 and self.game.player().ships[1].plan != Plan.ALIVE:
                                self.game.make_beam = BeamState.BOSS_SELECTED
                        else:
                            # See if there's cargo to take and set those ships up on a launch plan as well
                            loaded = 0

                            if self.game.enemy_at(position).is_captor():
                                loaded += 1
                                self.attackers.add_attacker(2, self.game.player().captured_fighter.position_index)

                            for i in range(3):
                                if self.game.enemy_at(position + 5 + i).plan == Plan.GRID:
                                    loaded += 1
                                    self.attackers.add_attacker(2, position + 5 + i)
                                if loaded == 2:
                                    break
                        # a boss added so stop looking
                        break

            # after boss pick, if still a slot, try to pick a bee or butterfly
            if self.attackers.count < 2:
                for position in gAttack_order:
                    # if idle
                    if self.game.enemy_at(position).plan == Plan.GRID:
                        self.attackers.add_attacker(0, position)
                        # Exit loop as an enemy was put in a slot
                        break

            # launch any attackers that haven't launched yet
            # This is done as a second part so that the initial primed 2 non-boss
            # attackers will get launched in this way
            for i in range(self.attackers.count):
                position = self.attackers.get_at(i)
                if position != -1:
                    # is this enemy idle or has it launched
                    enemy = self.game.enemy_at(position)
                    if enemy.plan == Plan.GRID:
                        # Make it launch if it was still idle
                        kind = enemy.entity_type
                        a_boss = (kind == EntityType.BOSS_GREEN) or (kind == EntityType.BOSS_BLUE)
                        cargo = (i >= 2)

                        if a_boss or cargo:
                            if self.game.make_beam == BeamState.BOSS_SELECTED:
                                self.game.make_beam += 1
                                # Put the make a beam action in here
                                enemy.next_plan = Plan.GOTO_BEAM
                            else:
                                # Put the BOSS and his cargo on their plan here
                                enemy.next_plan = Plan.PATH
                        else:
                            enemy.next_plan = Plan.PATH

                        enemy.plan = Plan.PATH
                        enemy.path_index = PATH_LAUNCH + gMirror[enemy.position_index]
                        enemy.attack_index = i
                        enemy.next_path_point()
                        self.game.sfx_stop(SOUND_DIVE_ATTACK)
                        self.game.sfx_play(SOUND_DIVE_ATTACK)
                        self.attackers.set_delay_timer(ATTACK_DELAY_TIME)
                        # if one of the 1st 2 and not a boss, launch only 1 - boss may have cargo later in array
                        if not (cargo or a_boss):
                            break


class AttractState(GameState):
    class Substate(IntEnum):
        TITLE = 1,
        SHOW_VALUES = 2,
        SHOW_COPYRIGHT = 3,
        SHOW_PLAY = 4,
        SHOW_SCORES = 5,
        HAVE_CREDIT = 6

    def __init__(self, game, substate):
        super().__init__(game)
        self.__game = game
        self.__state_timer = 0.0
        self.__spawner = None
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

    def update(self):
        self.do_attract_sequence()
        if (self.game.start == 1 and self.game.num_credits) or (self.game.start == 2 and self.game.num_credits > 1):
            self.game.num_players = self.game.start
            self.game.use_credits()
            self.game.set_text_range_visible(TEXT_GALAGA, TEXT_END_GAME_TEXT, False)
            self.game.set_sprite_range_visible(0, len(self.game.sprites) - 1, False)
            self.game.change_state(PlayingState(self.game, PlayingState.Substate.InitGame))

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
