import os

from Box2D import b2PolygonShape

from galaga.transform import TransformService
from galaga_data import *
from background import StarsService
from fxservice import RunningFxService
from attack import AttackService
from entities import Enemy, Bullet, Player
from play import PlayingState
from hwstartup import HwStartupState
from attract import AttractState
from tests import TestPath
from spawn import EnemySpawner

from pyjam.application import *
from pyjam.sprite import Sprite
from pyjam.sprites.animation import Animation2D
from pyjam.sprites.frame import SpriteFrame
from pyjam.sprites.sheet import SpriteSheet
from pyjam.text import Text, TextAlignment


# Arcade Longplay [535] Galaga
# https://www.youtube.com/watch?v=29VVkfuXkVI
class Galaga(Game):
    def __init__(self):
        super().__init__()

        self.set_assets_root('./assets')

        # if True run the game in exclusive fullscreen
        self.go_fullscreen = False

        # if True skip the initial hardware setup sequence
        self.skip_hw_startup = False

        # if True spawn waves as fast as possibile - use it only to accelerate testing ;)
        self.fast_spawn = False

        # -------------
        # cheats
        # -------------
        # self-explanatory
        self.invulnerability = False

        # self-explanatory
        self.infinite_lives = False

        # -------------
        # services
        # -------------
        self.stars_svc = StarsService(self)

        self.ent_svc = EntitiesService()

        self.fx_svc = RunningFxService(self)

        self.attack_svc = AttackService(self)

        self.spawner = EnemySpawner(self)

        self.transform_svc = TransformService()

        # [player1,player2]
        self.players = [Player(), Player()]

        self.num_players = 0

        self.current_player_idx = 0

        self.quiescence = False

        # storage for all on-screen enemies[player1, player2]
        # declare a matrix => enemies[2][MAX_ENEMIES]
        self.enemies = [[Enemy() for y in range(MAX_ENEMIES)] for x in range(2)]

        # all bullets possible on-screen (18)
        # the first 4 bullets are blue, the others are red
        self.bullets = [Bullet() for x in range(18)]

        # next slot to use for enemy bullet
        self.bullet_index = 0

        self.make_beam = BeamState.OFF

        self.bug_attack_speed = 0.0

        # ------------------
        # input
        # ------------------
        self.direction = 0
        self.fire = 0
        # used in Highscore substate
        self.managed_dir = 0
        self.prev_direction = 0
        self.repeat_delay = 0.0
        # (1 or 2) pressed start 1UP or 2UP
        self.start = 0
        # true when an add-credits button pressed
        self.coin_dropped = False
        # coins active in coin slot - always goes to 2
        self.num_credits = 0

        self.flash_timer = 0.0
        self.flash_index = [TEXT_1UP, TEXT_2UP]

        self.score_index = [TEXT_SCORE1P, TEXT_SCORE2P]

        self.enemies_killed_this_stage = 0

        # press F1 to show/hide FPS
        self.fps_text = None

        # leaderboard
        self.leaderboard = Leaderboard()

    def player(self):
        """
        Returns the current player
        """

        return self.players[self.current_player_idx]

    def enemy_at(self, enemy_idx):
        """
        Returns the enemy entity for the current player and at the given index
        """

        return self.enemies[self.current_player_idx][enemy_idx]

    def get_first_sprite_by_ent_type(self, ent_type: EntityType):
        return self.sprites[self.ent_svc.get_sprite_offset(ent_type)]

    def get_sprite_at_by_ent_type(self, ent_type: EntityType, idx: int):
        return self.sprites[self.ent_svc.get_sprite_offset(ent_type) + idx]

    def get_first_free_sprite_by_ent_type(self, ent_type: EntityType, player_idx: int):
        """ returns the first free sprite for the given entity type and mark the sprite as used """
        return self.sprites[self.ent_svc.get_first_free_sprite_idx(ent_type, player_idx)]

    def instantiate_state(self, state_name):
        if state_name == 'AttractState':
            return AttractState(self)
        elif state_name == 'HwStartupState':
            return HwStartupState(self)
        elif state_name == 'PlayingState':
            return PlayingState(self)
        else:
            raise AssertionError(f'Unknown state name: {state_name}')

    def setup_display(self):
        # Get the largest screen in aspect ratio that will fit the device
        # after leaving some room for a title bar, task bar, etc
        w = pg.display.get_desktop_sizes()[0][0] * ROOM_FOR_TITLE / ORIGINAL_X_CELLS
        h = pg.display.get_desktop_sizes()[0][1] * ROOM_FOR_TITLE / ORIGINAL_Y_CELLS
        if w < h:
            scale = w
        else:
            scale = h

        self.set_virtual_display_resolution(ORIGINAL_X_CELLS * ORIGINAL_CELL_RESOLUTION,
                                            ORIGINAL_Y_CELLS * ORIGINAL_CELL_RESOLUTION)

        flags = flags = pg.DOUBLEBUF | pg.RESIZABLE | pg.OPENGL
        if self.go_fullscreen:
            flags |= pg.FULLSCREEN
            sw = 1920
            sh = 1080
        else:
            sw = int(ORIGINAL_X_CELLS * scale)
            sh = int(ORIGINAL_Y_CELLS * scale)

        self.set_display_resolution(sw, sh, flags=flags)

        self.set_framerate(FRAME_RATE)

        pg.display.set_caption('pyjam-galaga')
        self.set_bg_color(pg.Color('black'))

    def initialize(self):
        asset_service = self.services[ASSET_SERVICE]

        font_sp_sheet = SpriteSheet(self)
        font_sp_sheet.load_rects('fonts/font.png')

        texture_service = self.services[TEXTURE_SERVICE]

        assets_sp_sheet = SpriteSheet(self)
        assets_sp_sheet.load_rects('textures/galaga-spritesheet.png')

        white_frame = SpriteFrame(texture_service.create_color_texture(pg.Color('white')))
        asset_service.insert('textures/star', white_frame)
        self.stars_svc.create_stars(NUM_STARS)
        self.stars_svc.disable()

        # create sprites
        entity_offset = len(self.sprites)
        for et in EntityType:
            sprites_needed = self.ent_svc.get_sprite_numbers(et)
            for j in range(sprites_needed):
                ent_data = self.ent_svc.get_entity_data(et)
                frames_list = Galaga.get_frames(ent_data.frame_name, ent_data.frame_numbers)
                frame = assets_sp_sheet.frames[frames_list[0]]
                sprite = Sprite(frame)

                # frames are double in size compared to the original ones
                sprite.size = glm.vec2(frame.width / 2, frame.height / 2)
                sprite.visible = False
                if ent_data.shape_size != (0, 0):
                    sprite.shape = b2PolygonShape(box=(ent_data.shape_size[0] / 2,
                                                       ent_data.shape_size[1] / 2))

                if len(frames_list) > 1:
                    animation = Animation2D()
                    for frame in frames_list:
                        animation.add_frame(assets_sp_sheet.frames[frame])
                    sprite.set_animation(animation)
                    sprite.play(fps=2, loop=True)

                self.sprites.append(sprite)

            self.ent_svc.set_sprite_offset(et, entity_offset)
            entity_offset += sprites_needed

        self.get_first_sprite_by_ent_type(EntityType.NAMCO).position = pc2v(glm.vec2(50, 91))

        # create text
        for t in g_texts_data:
            self.texts.append(self.create_text(t[1], t[2], t[3], t[4]))

        # setup lives positions
        for i in range(2, self.ent_svc.get_sprite_numbers(EntityType.FIGHTER)):
            sprite = self.get_sprite_at_by_ent_type(EntityType.FIGHTER, i)
            hx = sprite.hotspot.x
            hy = sprite.hotspot.y
            sprite.position.x = pcx2vx((2 * (i - 1) / ORIGINAL_X_CELLSF) * 100.0) - hx
            sprite.position.y = pcy2vy(((ORIGINAL_Y_CELLSF - 3) / ORIGINAL_Y_CELLSF) * 100.0) - hy

        # load sounds fx
        for sound_name in g_sfx:
            file = os.path.join(self.get_assets_root(), f'sfx/{sound_name}.wav')
            self.add_sfx(sound_name, pg.mixer.Sound(file))

        # set up the player bullets
        for i in range(self.ent_svc.get_sprite_numbers(EntityType.BLUE_BULLET)):
            sprite = self.get_sprite_at_by_ent_type(EntityType.BLUE_BULLET, i)
            self.bullets[i].sprite = sprite
            self.bullets[i].kind = EntityType.BLUE_BULLET
            self.bullets[i].plan = Plan.DEAD

        # set up the enemy bullets
        for i in range(self.ent_svc.get_sprite_numbers(EntityType.RED_BULLET)):
            sprite = self.get_sprite_at_by_ent_type(EntityType.RED_BULLET, i)
            # red bullet sprites start just after the last blue bullet sprite
            bullet_idx = self.ent_svc.get_sprite_numbers(EntityType.BLUE_BULLET) + i
            self.bullets[bullet_idx].sprite = sprite
            self.bullets[bullet_idx].kind = EntityType.RED_BULLET
            self.bullets[bullet_idx].plan = Plan.DEAD

        # try to load leaderboards for filesystem
        if os.path.exists(Leaderboard.filename):
            self.leaderboard.load()
        else:
            # otherwise load default leaderbord
            for i in range(len(self.leaderboard.high_scores)):
                self.leaderboard.high_scores[i].name = g_texts_data[TEXT_N_N + i][1]
                self.leaderboard.high_scores[i].score = int(g_texts_data[TEXT_SCORE_1 + i][1])

        # update leaderboard texts
        for i in range(len(self.leaderboard.high_scores)):
            self.texts[TEXT_N_N + i].text = self.leaderboard.high_scores[i].name
            self.texts[TEXT_SCORE_1 + i].text = self.format_score(self.leaderboard.high_scores[i].score)

        # update highscore text
        self.texts[TEXT_20000].text = str(self.leaderboard.high_scores[0].score)

        self.stars_svc.speed = STAR_MAX_SPEED
        self.num_credits = 0

        self.set_text_range_visible(TEXT_GALAGA, TEXT_END_GAME_TEXT, False)
        self.set_sprite_range_visible(0, len(self.sprites) - 1, False)

        # create FPS text
        self.fps_text = self.create_text("00", (100, 0), COLOR_WHITE, TextAlignment.RIGHT)
        self.fps_text.visible = False
        self.texts.append(self.fps_text)

        if self.skip_hw_startup:
            self.change_state(self.instantiate_state('AttractState'))
        else:
            self.change_state(self.instantiate_state('HwStartupState'))

    @staticmethod
    def get_frames(base_frame_name, frames_count):
        if frames_count > 1:
            return [f'{base_frame_name}_{i}' for i in range(1, frames_count + 1)]
        else:
            return [base_frame_name]

    def set_text_range_visible(self, range_start, range_end, vis_flag):
        for i in range(range_start, range_end + 1):
            self.texts[i].visible = vis_flag

    def set_sprite_range_visible(self, range_start, range_end, vis_flag):
        """ When passing a len as range_end, you have to pass len()-1, otherwise pass the value as is """
        for i in range(range_start, range_end + 1):
            self.sprites[i].visible = vis_flag

    def update(self):
        # hw-startup state
        if isinstance(self.state, HwStartupState) and self.state.substate == HwStartupState.Substate.END_HW_STARTUP:
            self.change_state(self.instantiate_state('AttractState'))
        # attract or play state
        else:
            self.process_input()
            self.update_fps_text()

            if self.coin_dropped:
                self.sfx_play(SOUND_COIN_DROPPED)
                self.add_credit()
                if isinstance(self.state, AttractState):
                    self.state.substate = AttractState.Substate.HAVE_CREDIT

            if isinstance(self.state, PlayingState) and self.state.is_game_over():
                self.change_state(self.instantiate_state('AttractState'))
                self.set_sprite_range_visible(0, self.ent_svc.get_sprite_offset(EntityType.RED_BULLET), False)

        super().update()

    def update_fps_text(self):
        fps = self.clock.get_fps()
        if fps < 59:
            fps_color = 'red'
        else:
            fps_color = 'green'

        self.fps_text.text = f'{fps:.0f}'
        self.fps_text.color = pg.Color(fps_color)

    def process_input(self):
        if isinstance(self.state, HwStartupState):
            return

        self.direction = 0
        self.fire = 0
        self.coin_dropped = False
        self.start = 0

        if self.key_down(pg.K_LEFT):
            self.direction = -1

        if self.key_down(pg.K_RIGHT):
            self.direction = 1

        if self.key_pressed(pg.K_LCTRL):
            self.fire = 1

        if self.key_pressed(pg.K_RETURN):
            self.coin_dropped = True

        if self.key_pressed(pg.K_1):
            self.start = 1

        if self.key_pressed(pg.K_2):
            self.start = 2

        if self.key_pressed(pg.K_F1):
            self.fps_text.visible = not self.fps_text.visible

        if self.key_pressed(pg.K_ESCAPE):
            self.signal_quit()

        if self.key_pressed(pg.K_t):
            if isinstance(self.state, AttractState):
                self.change_state(TestPath(self))
            elif isinstance(self.state, TestPath):
                self.change_state(AttractState(self))

        if self.prev_direction == self.direction:
            self.repeat_delay -= self.delta_time
            if self.repeat_delay > 0.0:
                self.managed_dir = 0
            else:
                self.managed_dir = self.direction
                self.repeat_delay = REPEAT_DELAY
        else:
            self.prev_direction = self.direction
            self.managed_dir = self.direction
            self.repeat_delay = REPEAT_INITIAL_DELAY

    def create_text(self, txt, position, color, alignment):
        text = Text(txt, self.services[ASSET_SERVICE].get('fonts/font'))
        text.size = pc2v(glm.vec2(TEXT_SIZE * (ORIGINAL_Y_CELLSF / ORIGINAL_X_CELLSF), TEXT_SIZE))
        text.color = pg.Color(color)
        text.visible = False
        text.position = pc2v(glm.vec2(position))
        text.alignment = alignment
        return text

    def increment_score(self, amount):
        old_score = self.player().score
        new_score = old_score + amount

        # under 1M points, give life at 20k and every 70k
        if new_score < 1000000:
            if (old_score < 20000 and new_score >= 20000) or (old_score // 70000) < (new_score // 70000):
                self.player().lives += 1
                self.state.show_lives_icons()
                self.sfx_play(SOUND_EXTRA_LIFE)

        self.player().score = new_score

        self.texts[self.score_index[self.current_player_idx]].text = self.format_score(self.player().score)
        if self.player().score > self.leaderboard.high_scores[0].score:
            self.texts[TEXT_20000].text = self.format_score(self.player().score)

    def add_credit(self):
        self.num_credits += 1
        if self.num_credits > 9:
            vis_credit = 9
        else:
            vis_credit = self.num_credits
        self.texts[TEXT_0].text = str(vis_credit)

    def use_credits(self):
        self.num_credits -= self.start
        self.texts[TEXT_0].text = str(self.num_credits)
        self.start = 0

    def is_gameplay_running(self):
        return isinstance(self.state, PlayingState) and self.state.substate >= PlayingState.Substate.Play

    def move_bullets(self):
        for bullet in self.bullets:
            if bullet.plan == Plan.ALIVE:
                sprite = bullet.sprite
                if bullet.kind == EntityType.BLUE_BULLET:
                    # TODO: Player bullets only travel in astraight line but
                    #   when the player is being beamed, the bullets can go at an
                    #   angle - add support for that
                    bullet.y -= BULLET_SPEED * self.delta_time
                    if bullet.y < (1 / ORIGINAL_Y_CELLSF) * 100:
                        bullet.plan = Plan.DEAD
                        sprite.visible = False
                else:
                    tx = self.delta_time * bullet.velocity.x
                    ty = self.delta_time * bullet.velocity.y

                    # update the position
                    bullet.x -= tx
                    bullet.y -= ty

                    if bullet.y > ((ORIGINAL_Y_CELLSF - 2) / ORIGINAL_Y_CELLSF) * 100.0:
                        bullet.plan = Plan.DEAD
                        bullet.sprite.visible = False
                    else:
                        if self.player().was_hit(sprite):
                            bullet.plan = Plan.DEAD
                            sprite.visible = False

                sprite.position = pc2v(glm.vec2(bullet.x, bullet.y))

    @staticmethod
    def format_score(score: int) -> str:
        return '{:7d}'.format(score)
