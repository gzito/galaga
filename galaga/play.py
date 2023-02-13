import copy
import glm

from pyjam.application import GameState, pc2v, pcx2vx, pcy2vy, vx2pcx, vy2pcy
from galaga_data import *


class PlayingState(GameState):
    class Substate(IntEnum):
        InitGame = 1
        StageInit = 2
        StageIconsInit = 3
        PreShowField = 4
        StageIcons = 5
        PlayerInit = 6
        PrePlay = 7
        Play = 8
        StageClear = 9
        PlayerDied = 10
        HideField = 11
        NextToPlay = 12
        ShowField = 13
        ShowChallengeResults = 14
        PlayerGameOver = 15
        ShowGameOverStats = 16
        HoldGameOverStats = 17
        HighScore = 18
        HoldHighScore = 19

    def __init__(self, game, substate=None):
        super().__init__(game)

        self.__state_timer = 0.0
        if substate is None:
            self.__substate = PlayingState.Substate.InitGame
        else:
            self.__substate = substate
        self.__scratch1 = 0
        self.__scratch2 = 0
        self.__game_over = False

    @property
    def substate(self):
        return self.__substate

    @substate.setter
    def substate(self, new_state):
        self.__substate = new_state
        self.__scratch1 = 0
        self.__scratch2 = 0
        self.__state_timer = 0.0

    def is_game_over(self):
        return self.__game_over

    def update(self):
        self.game.player().update()
        self.game.move_bullets()
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
                self.game.spawner.setup_new_stage()
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
                self.game.attack_svc.bugs_attack = False
                self.game.attack_svc.attackers.clear_all()
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
                    self.game.spawner.run()
                if not self.game.attack_svc.bugs_attack:
                    self.game.attack_svc.bugs_attack = self.game.attack_svc.attack_ready()
                if self.game.attack_svc.bugs_attack:
                    self.game.attack_svc.choose_attacker()
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
                if self.game.spawner.spawn_wave:
                    self.game.spawner.run()
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
                            self.game.texts[TEXT_SCORE_1 + lb.edit_score + 1].text = \
                                self.game.texts[TEXT_SCORE_1 + lb.edit_score].text
                            self.game.texts[TEXT_N_N + lb.edit_score + 1].text = \
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

                lb.entry.name = lb.entry.name[0:lb.edit_letter] + chr(letter) + lb.entry.name[lb.edit_letter + 1:]
                self.game.texts[TEXT_INITALS_INITIALS].text = lb.entry.name

            # On fire, lock in an initial - 3 locked in ends the sequence
            if self.game.fire:
                self.game.texts[TEXT_INITALS_INITIALS].set_char_color(lb.edit_letter, COLOR_RED)
                self.game.texts[TEXT_N_N + lb.edit_score].text = lb.entry.name[0:lb.edit_letter + 1]
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
        player.lives = self.game.num_of_lives
        player.stage = self.game.initial_stage
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
