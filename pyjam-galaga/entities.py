from Box2D import b2PolygonShape

from random import randint
from fxservice import RunningFx, RunningFxSequence
from galaga_data import *
from pyjam import utils
from pyjam.application import Game, pc2v, pcy2vy, vx2pcx, vy2pcy
from pyjam.core import Bounds
from pyjam.utils import *


class Entity:
    def __init__(self):
        # the type of entity
        self.entity_type = None

        # sprite object
        self.sprite = None

        #  if an enemy, where in the grid should it go
        self.position_index = 0

        # what the entity should be doing
        self.plan = 0

        # what the entity will do next
        self.next_plan = 0

        # index into PlayGameState.attackers when attacking
        self.attack_index = 0

        # entity position
        self.x = 0.0
        self.y = 0.0

        # rotation (angle)
        self.rotation = 0.0

        # position of the next target point relative to entity position, i.e. delta from entity position
        self.delta_dest = glm.vec2(0.0)

        # when following a path, which path
        self.path_index = 0

        # heading to which point in the path
        self.point_index = 0

        # velocity
        self.velocity = glm.vec2(0.0)

        # angle to the destination
        self.dr = 0.0

        # increment angle (rate of turn)
        self.ir = 0.0

        # distance remaining to next point
        self.distance = 0.0

        # if an enemy, prepare to shoot
        self.shots_to_fire = 0

        # a timer used to delay next actions, in secs (seconds with fractional part)
        self.timer = 0.0

    """
    @property
    def position(self) -> glm.vec2:
        return self.__position

    @position.setter
    def position(self, value: glm.vec2):
        self.__position = glm.vec2(value)

    @property
    def x(self) -> float:
        return self.__position.x

    @x.setter
    def x(self, value: float):
        self.__position.x = value

    @property
    def y(self) -> float:
        return self.__position.y

    @y.setter
    def y(self, value: float):
        self.__position.y = value
    """


class Grid:
    def __init__(self):
        # grid timer
        self.__timer = 0.0

        # grid direction, 1 or -1
        self.__dir = 1.0

        # 0 = grid is not breathing, 1 = grid is breathing
        self.__breathing = 0

        # this is used during the sequence exchange of player 1 & 2
        self.__y_offset = 0.0

        self.__time = [WALK_TIME, BREATHE_TIME]

    @property
    def timer(self):
        return self.__timer

    @property
    def breathing(self):
        return self.__breathing

    @breathing.setter
    def breathing(self, value: int):
        self.__breathing = value
        if value:
            # not this sound in challenge stage
            if Game.instance.player().stage_index < 3:
                Game.instance.sfx_play(SOUND_BREATHING_TIME, -1)
            else:
                Game.instance.sfx_stop(SOUND_BREATHING_TIME)
        else:
            Game.instance.sfx_stop(SOUND_BREATHING_TIME)

    @property
    def y_offset(self):
        return self.__y_offset

    @y_offset.setter
    def y_offset(self, value):
        self.__y_offset = value

    def reset(self):
        self.__timer = 0.0
        self.__dir = 1.0
        self.__breathing = 0
        self.__y_offset = 0.0

    def update(self, delta_time):
        old_timer = self.__timer
        self.__timer += delta_time * self.__dir
        if self.__timer >= self.__time[self.__breathing] or self.__timer <= 0:
            # At extents, flip direction
            self.__dir = -self.__dir
            # but step back into range so there's no chance of getting
            # stuck outside the range on a smaller delta-time next frame
            self.__timer += delta_time * self.__dir

        # After walking left/right, activate breathing when the grid is in the middle
        if not self.__breathing:
            if not Game.instance.player().spawn_active:
                middle = self.__time[0] / 2.0
                s1 = middle - old_timer
                s2 = middle - self.__timer
                # if this is < 0 the signs are not the same meaning the gris crossed just over the middle
                if s1 * s2 < 0:
                    self.__breathing = 1
                    self.__timer = 0.0
                    self.__dir = 1.0


class Player:
    def __init__(self):
        self.ships = [Entity(), Entity()]

        # lives player has in reserve
        self.lives = 0

        # current player score
        self.score = 0

        # current player stage
        self.stage = 0

        self.stage_icons_to_show = []

        self.stage_icons_shown = []

        # the wave to spawn (0-4)
        self.attack_wave = 0

        # the index (0-3) into gSpawnOrder[wave,side], one for each side
        self.spawn_index = [0, 0]

        # the side (0-1) at which to spawn the next enemy
        self.kind_index = 0

        # used as index for gPathIndicies
        self.stage_index = 0

        # enemy spawn is active or not
        self.spawn_active = False

        # number of enemies to kill in the stage
        self.enemies_alive = 0

        # number of shots fired
        self.shots_fired = 0

        # number of enemies taken down
        self.hits = 0

        self.__grid = Grid()

        # capture variables
        self.__capture_state = CaptureState.OFF

        # the captured fighter entity
        self.__captured_fighter = None

        # the boss entity which captured the fighter
        self.__captor_boss = None

        self.__rescued_ship = None
        self.__rescued_ship_dest = glm.vec2()

    @property
    def grid(self):
        return self.__grid

    @property
    def capture_state(self) -> CaptureState:
        return self.__capture_state

    @capture_state.setter
    def capture_state(self, value: CaptureState):
        self.__capture_state = value

    @property
    def captured_fighter(self):
        return self.__captured_fighter

    @captured_fighter.setter
    def captured_fighter(self, value):
        self.__captured_fighter = value

    def get_captor_boss(self) -> Entity:
        return self.__captor_boss

    def set_captor_boss(self, boss_ent: Entity):
        self.__captor_boss = boss_ent

    def clear_captor_boss(self):
        if self.__captor_boss:
            self.__captor_boss.set_captor(False)
        self.__captor_boss = None

    def is_capturing(self) -> bool:
        return CaptureState.OFF < self.capture_state < CaptureState.CAPTURE_COMPLETE

    def is_captured(self) -> bool:
        return self.capture_state >= CaptureState.FIGHTER_CAPTURED

    def swap_ships(self):
        # when player 1 is alive and 0 dead, assign 1 to 0 so 0 is always the one that's alive
        self.ships[0].x = self.ships[1].x
        self.ships[0].y = self.ships[1].y
        self.ships[0].plan = Plan.ALIVE
        self.ships[0].sprite.visible = True
        self.ships[1].plan = Plan.DEAD
        self.ships[1].sprite.visible = False

    def kill(self, ship_num):
        """
        Player.kill() subroutine
        """
        ship = self.ships[ship_num]
        ship.plan = Plan.DEAD
        ship.sprite.visible = 0

        Game.instance.sfx_play(SOUND_PLAYER_DIE)

        # if both ships are dead stop the starfield
        if self.ships[0].plan == Plan.DEAD and self.ships[1].plan == Plan.DEAD:
            Game.instance.stars_svc.speed = 0

        sprite = Game.instance.get_first_sprite_by_ent_type(EntityType.FIGHTER_EXPLOSION)

        sprite.position = pc2v(glm.vec2(ship.x, ship.y))
        sprite.visible = True
        sprite.play(True, PLAYER_EXPLOSION_FPS)

        frames = Game.instance.ent_svc.get_entity_data(EntityType.FIGHTER_EXPLOSION).frame_numbers
        running_effect = RunningFx(sprite, frames * (1.0 / (PLAYER_EXPLOSION_FPS - 1)))
        Game.instance.fx_svc.insert(running_effect)

    def handle_capture(self):
        # FIGHTER_TOUCHED
        if self.capture_state == CaptureState.FIGHTER_TOUCHED:
            Game.instance.stars_svc.speed = STAR_CAPTURE_SPEED
            beam_x = vx2pcx(Game.instance.get_first_sprite_by_ent_type(EntityType.BEAM).x)
            offset_x = self.ships[0].x
            if offset_x < beam_x:
                offset_x += PLAYER_CAPTURED_SPEED * Game.instance.delta_time
            elif offset_x > beam_x:
                offset_x -= PLAYER_CAPTURED_SPEED * Game.instance.delta_time
            else:
                offset_x = beam_x

            self.ships[0].x = offset_x

            if self.ships[0].y > 67.5:
                self.ships[0].y -= PLAYER_CAPTURED_SPEED * Game.instance.delta_time
                self.ships[0].rotation += CAPTURE_SPIN_SPEED * Game.instance.delta_time

                self.ships[0].sprite.position = pc2v(glm.vec2(offset_x, self.ships[0].y))
                self.ships[0].sprite.angle = self.ships[0].rotation
            else:
                self.ships[0].rotation = 0
                self.ships[0].sprite.angle = self.ships[0].rotation
                Game.instance.sfx_stop(SOUND_BEAM_CAPTURED)
                ship_0 = self.ships[0]
                captured_entity = CapturedFighter()
                captured_entity.entity_type = EntityType.CAPTURED_FIGHTER
                captured_entity.x = ship_0.x
                captured_entity.y = ship_0.y
                captured_entity.rotation = ship_0.rotation
                captured_entity.sprite = Game.instance.get_first_sprite_by_ent_type(EntityType.CAPTURED_FIGHTER)
                captured_entity.sprite.position = ship_0.sprite.position
                captured_entity.sprite.angle = ship_0.sprite.angle
                captured_entity.sprite.visible = True
                captured_entity.plan = Plan.ALIVE
                captured_entity.attack_index = -1
                self.captured_fighter = captured_entity
                boss_entity = self.get_captor_boss()
                # sets the captured fighter position in the grid, one row just above the captor boss
                Game.instance.enemies[Game.instance.current_player_idx][
                    boss_entity.position_index - 4] = captured_entity
                ship_0.sprite.visible = False
                ship_0.timer = 2.0
                self.capture_state = CaptureState.DISPLAY_CAPTURED
        # DISPLAY_CAPTURED
        elif self.capture_state == CaptureState.DISPLAY_CAPTURED:
            self.ships[0].timer -= Game.instance.delta_time
            if self.ships[0].timer < 0:
                Game.instance.texts[TEXT_FIGHTER_CAPTURED].visible = True
                if Game.instance.sfx_get_num_channels(SOUND_BREATHING_TIME) > 0:
                    Game.instance.sfx_stop(SOUND_BREATHING_TIME)
                Game.instance.sfx_play(SOUND_PLAYER_CAPTURED, -1)
                self.ships[0].timer = 3.0
                self.capture_state = CaptureState.HOLD
        # HOLD
        elif self.capture_state == CaptureState.HOLD:
            Game.instance.stars_svc.speed = STAR_MAX_SPEED
            self.ships[0].timer -= Game.instance.delta_time
            if self.ships[0].timer < 0:
                Game.instance.texts[TEXT_FIGHTER_CAPTURED].visible = False
                self.capture_state = CaptureState.FIGHTER_CAPTURED
        # CAPTURE_COMPLETE - goto in this state when the captured fighter arrives to grid, see enemy.decision_time()
        elif self.capture_state == CaptureState.CAPTURE_COMPLETE:
            # fighter captured, so increase the number of enemies
            self.enemies_alive += 1
            Game.instance.sfx_stop(SOUND_PLAYER_CAPTURED)
            if Game.instance.sfx_get_num_channels(SOUND_BREATHING_TIME) <= 0:
                Game.instance.sfx_play(SOUND_BREATHING_TIME, -1)

            # if there are no more lives => the game is over
            if self.lives == 0:
                self.capture_state = CaptureState.READY
                self.ships[0].plan = Plan.DEAD
            else:
                self.captured_fighter.sprite.hotspot = glm.vec2(7, 8)
                self.ships[0].x = 50
                self.ships[0].y = ((ORIGINAL_Y_CELLSF - 3.0) / ORIGINAL_Y_CELLSF) * 100
                self.ships[0].plan = Plan.ALIVE
                self.ships[0].sprite.visible = True
                self.ships[0].sprite.position = pc2v(glm.vec2(self.ships[0].x, self.ships[0].y))
                if not Game.instance.infinite_lives:
                    self.lives -= 1
                Game.instance.state.show_lives_icons()
                self.ships[0].timer = 3
                Game.instance.texts[TEXT_READY].visible = True
                self.capture_state += 1
        # DISPLAY_READY
        elif self.capture_state == CaptureState.DISPLAY_READY:
            self.ships[0].timer -= Game.instance.delta_time
            if self.ships[0].timer < 0.0:
                Game.instance.texts[TEXT_READY].visible = False
                Game.instance.state.attackers.clear_all()
                self.capture_state += 1
        # READY
        elif self.capture_state == CaptureState.READY:
            # nothing to do here, it's just to signal the capture sequence as completed and the game can go on
            return
        # RESCUED
        elif self.capture_state == CaptureState.RESCUED:
            cap_fighter = self.captured_fighter
            ship_1 = self.ships[1]
            cap_fighter.plan = Plan.DEAD
            ship_1.x = cap_fighter.x
            ship_1.y = cap_fighter.y
            ship_1.sprite.visible = True
            ship_1.plan = Plan.ALIVE
            cap_fighter.sprite.visible = False

            Game.instance.state.attackers.clear_attacker(cap_fighter.attack_index)
            cap_fighter.attack_index = -1

            self.captured_fighter = None
            ship_1.sprite.position = pc2v(glm.vec2(ship_1.x, ship_1.y))

            if Game.instance.sfx_get_num_channels(SOUND_BREATHING_TIME) > 0:
                Game.instance.sfx_stop(SOUND_BREATHING_TIME)
            Game.instance.sfx_play(SOUND_CAPTURED_FIGHTER_RESCUED, -1)

            self.ships[1].timer = 2.0

            self.capture_state += 1
        # SPINNING
        elif self.capture_state == CaptureState.SPINNING:
            if not Game.instance.quiescence or self.ships[1].timer > 0:
                r = self.ships[1].rotation
                r += CAPTURE_SPIN_SPEED * Game.instance.delta_time
                self.ships[1].rotation = r
                self.ships[1].sprite.angle = r
                self.ships[1].timer -= Game.instance.delta_time
            else:
                self.capture_state += 1
        # DOCKING
        elif self.capture_state == CaptureState.DOCKING:
            # check if ship 0 is dead
            if self.__rescued_ship is None:
                if self.ships[0].plan == Plan.DEAD:
                    self.swap_ships()
                    self.__rescued_ship = self.ships[0]
                    self.__rescued_ship_dest.x = 50
                else:
                    self.__rescued_ship = self.ships[1]
                    self.__rescued_ship_dest.x = 50 + vx2pcx(self.ships[0].sprite.width)
                self.__rescued_ship_dest.y = ((ORIGINAL_Y_CELLSF - 3.0) / ORIGINAL_Y_CELLSF) * 100
                self.__rescued_ship.rotation = 0

            step = FIGHTER_RESCUED_MOVEMENT_SPEED * Game.instance.delta_time

            # if ships[1] is ALIVE then it is the rescued ship, so move also ships[0]
            if self.ships[1].plan == Plan.ALIVE:
                if self.ships[0].x > 50.0:
                    self.ships[0].x = utils.clamp(self.ships[0].x - step, 50.0, self.ships[0].x)
                elif self.ships[0].x < 50.0:
                    self.ships[0].x = utils.clamp(self.ships[0].x + step, self.ships[0].x, 50.0)

            # move rescued ship
            if self.__rescued_ship.x > self.__rescued_ship_dest.x:
                self.__rescued_ship.x = utils.clamp(self.__rescued_ship.x - step,
                                                    self.__rescued_ship_dest.x, self.__rescued_ship.x)
            elif self.__rescued_ship.x < self.__rescued_ship_dest.x:
                self.__rescued_ship.x = utils.clamp(self.__rescued_ship.x + step,
                                                    self.__rescued_ship.x, self.__rescued_ship_dest.x)
            elif self.__rescued_ship.y < self.__rescued_ship_dest.y:
                self.__rescued_ship.y = utils.clamp(self.__rescued_ship.y + step,
                                                    self.__rescued_ship.y, self.__rescued_ship_dest.y)
            else:
                self.__rescued_ship.y = self.__rescued_ship_dest.y
                Game.instance.sfx_stop(SOUND_CAPTURED_FIGHTER_RESCUED)
                if Game.instance.sfx_get_num_channels(SOUND_BREATHING_TIME) <= 0:
                    Game.instance.sfx_play(SOUND_BREATHING_TIME, -1)

                self.__rescued_ship = None
                Game.instance.state.attackers.clear_all()
                # fighter rescued, so decrease the number of enemies
                self.enemies_alive -= 1
                self.capture_state = CaptureState.OFF

            # update fighter(s) sprites
            if self.ships[0].plan == Plan.ALIVE:
                self.ships[0].sprite.position = pc2v(glm.vec2(self.ships[0].x, self.ships[0].y))
                self.ships[0].sprite.angle = self.ships[0].rotation
            if self.ships[1].plan == Plan.ALIVE:
                self.ships[1].sprite.position = pc2v(glm.vec2(self.ships[1].x, self.ships[1].y))
                self.ships[1].sprite.angle = self.ships[1].rotation

    def was_hit(self, sprite) -> bool:
        """
        Player.was_hit()

        Checks for collision between the fighter and enemy or red bullet sprite
        Also kills the fighter as needed
        """

        if not Game.instance.invulnerability:
            if not self.is_capturing() and not self.capture_state >= CaptureState.RESCUED:
                if self.ships[0].plan == Plan.ALIVE and not self.is_capturing():
                    if sprite.collide(self.ships[0].sprite):
                        self.kill(0)
                        return True

                if self.ships[1].plan == Plan.ALIVE:
                    if sprite.collide(self.ships[1].sprite):
                        self.kill(1)
                        return True
                    elif self.ships[0].plan == Plan.DEAD:
                        # if ships[1] is alive and ships[0] dead, assign 1 to 0 so 0 is always the one that's alive
                        self.swap_ships()
        return False


class Bullet(Entity):
    def __init__(self):
        super().__init__()


class Enemy(Entity):
    next_explosion = 0

    def __init__(self):
        super().__init__()
        self.__beam_height = 0.0
        self.__is_captor = False

    def set_captor(self, value: bool):
        self.__is_captor = value

    def is_captor(self) -> bool:
        return self.__is_captor

    def update(self, delta_time: float):
        if self.plan != Plan.GRID:
            Game.instance.quiescence = False

        if self.plan == Plan.BEAM_ACTION:
            self.run_beam_action()
            return

        # if plan is GOTO_GRID, ORIENT or GRID => the destination is the grid
        if Plan.GOTO_GRID <= self.plan <= Plan.GRID:
            self.get_grid_coordinate()

        # Calculate how much to move this frame in each axis
        t = delta_time * self.velocity
        # figure out what that is along the vector
        dist = glm.length(t)

        # Butterflies flutter on an ARC
        if self.plan == Plan.FLUTTER:
            # get the current angle
            r = self.rotation - 90.0
            # save the angle
            ro = r
            # adjust for the increment
            r += self.ir * delta_time
            # see if desired angle reached and stop changing
            if (r - ro) * (self.dr - ro) < 0.0:
                self.ir = 0.0
            # get the x/y step sizes
            t.x = delta_time * Game.instance.bug_attack_speed * utils.cos_deg(r)
            t.y = delta_time * Game.instance.bug_attack_speed * utils.sin_deg(r)

            # set the facing angle in the Entity and the sprite
            self.rotation = r + 90.0
            self.sprite.angle = self.rotation
        else:
            # See how far along the path, and clip to not overshoot
            if dist > self.distance:
                t = self.delta_dest

        self.x += t.x
        self.y += t.y

        # update the distance to travel components
        self.delta_dest -= t
        self.distance -= dist

        if self.plan != Plan.GRID and self.distance <= 0.0:
            self.decision_time()

        if self.timer > 0:
            self.timer -= Game.instance.delta_time
            if self.timer <= 0.0:
                if self.shots_to_fire:
                    self.fire()
                    self.shots_to_fire -= 1
                    if self.shots_to_fire != 0:
                        self.timer = ENEMY_GUN_RELOAD_TIME

        # Put the enemy where it wants to go
        self.sprite.position = pc2v(glm.vec2(self.x, self.y))

    def get_grid_coordinate(self):
        grid_y_coords = [0, 18, 36, 48, 60, 72]

        col = gGrid_cols[self.position_index]
        row = gGrid_rows[self.position_index]

        player = Game.instance.player()
        h = grid_y_coords[row]
        if player.grid.breathing:
            # how much the grid expands along x and y
            breathe_x = 1.418 * player.grid.timer
            breathe_y = 0.675 * player.grid.timer

            n = glm.vec2(19.85 + (col * 6.7) + (col - 5) * breathe_x, 11.05 + (vy2pcy(h)) + (row + 1) * breathe_y)
        else:
            walk_x = 9.925 * player.grid.timer
            n = glm.vec2((col * 6.7) + walk_x, 11.05 + vy2pcy(h))
        # grid_y_offset is 0 during the game play, it's changed during show-field and hide-field phases,
        # when exchanging from player 1 & 2
        n.y += player.grid.y_offset

        self.delta_dest.x = n.x - self.x
        self.delta_dest.y = n.y - self.y

        self.setup_velocity_and_rotation()

    def setup_velocity_and_rotation(self):
        if not Game.instance.state.bugs_attack:
            if not Game.instance.fast_spawn:
                speed = BUG_TRAVEL_SPEED
            else:
                speed = BUG_TRAVEL_SPEED * 5
        else:
            speed = Game.instance.bug_attack_speed

        if self.plan == Plan.PATH:
            index = self.path_index >> 1
            if index == aPath_Bottom_Double_Out:
                if self.point_index > 4:
                    speed = speed * 1.625
                else:
                    speed = speed * 1.1
            elif index == aPath_Top_Double_Left:
                if self.point_index > 4:
                    speed = speed * 1.625

        # How far to travel and at what angle
        self.distance = glm.length(self.delta_dest)
        r = vec2_angle_from_y_deg(self.delta_dest)

        # set the enemy rotation only if it's not about to land in the grid and is not in the grid.
        # That's because the grid causes left/right motion that leads to extreme rotation which this ignores
        if self.plan < Plan.ORIENT or self.plan > Plan.GRID:
            # if the enemy is about to land in the grid, don't change its angle as that looks bad
            if not (abs(self.delta_dest.y) < 3.0 and self.plan == Plan.GOTO_GRID):
                self.rotation = r

        # the velocity along the vectors
        self.velocity = vec2_from_angle_deg(r) * speed

        # point the sprite at the desired direction
        self.sprite.angle = self.rotation

    def decision_time(self):
        # Reached the grid
        if self.plan == Plan.GOTO_GRID:
            if Game.instance.player().ships[0].plan == Plan.ALIVE and \
                    not Game.instance.player().spawn_active and \
                    not Game.instance.player().capture_state >= CaptureState.RESCUED and \
                    Game.instance.player().enemies_alive < 5:
                # keep attacking straight away
                # TODO - I think this is actually right at the top of the screen, not here at the grid level
                self.plan = Plan.PATH
                if self.entity_type == EntityType.BEE:
                    self.path_index = PATH_BEE_ATTACK + gMirror[self.position_index]
                    self.next_plan = Plan.DESCEND
                else:
                    self.path_index = PATH_BUTTERFLY_ATTACK + gMirror[self.position_index]
                    self.next_plan = Plan.FLUTTER

                self.next_path_point()
            else:
                # rotate in place
                self.plan = Plan.ORIENT
        # keep rotating till zero facing, then just be in the grid
        elif self.plan == Plan.ORIENT:
            # Take out of attack mode when arriving in the grid
            if self.attack_index >= 0:
                Game.instance.state.attackers.clear_attacker(self.attack_index)
                self.attack_index = -1

            if self.rotation < -GRID_ORIENT_ANGLE:
                self.rotation += GRID_ORIENT_ANGLE
            elif self.rotation > GRID_ORIENT_ANGLE:
                self.rotation -= GRID_ORIENT_ANGLE
            else:
                self.rotation = 0
                self.plan = Plan.GRID
                # if this enemy is the captured fighter returning to the grid => the capture sequence is COMPLETE
                if self is Game.instance.player().captured_fighter:
                    if CaptureState.OFF < Game.instance.player().capture_state < CaptureState.CAPTURE_COMPLETE:
                        Game.instance.player().capture_state = CaptureState.CAPTURE_COMPLETE
        # end of a point in the path, maybe the end of the path
        elif self.plan == Plan.PATH:
            self.point_index += 1
            if self.point_index < len(gPathData[self.path_index >> 1]):
                self.next_path_point()
            else:
                self.point_index = 0
                self.decision_on_post_path()
        # After descend, start the bottom half circle path
        elif self.plan == Plan.DESCEND:
            self.plan = Plan.PATH
            self.path_index = PATH_BEE_BOTTOM_CIRCLE + gMirror[self.position_index]
            self.next_path_point()
            # Set up for deciding what to do at the end of that bottom circle
            self.next_plan = Plan.HOME_OR_FULL_CIRCLE
        elif self.plan == Plan.FLUTTER:
            if self.y < 100:
                self.setup_flutter_arc()
            else:
                self.plan = Plan.DIVE_ATTACK
                self.delta_dest.x = 0
                self.delta_dest.y = 3
                self.next_plan = Plan.GOTO_GRID
                self.setup_velocity_and_rotation()
        # Out the bottom so go away
        elif self.plan == Plan.DIVE_AWAY:
            self.plan = Plan.DEAD
            Game.instance.player().enemies_alive -= 1
            self.sprite.visible = False
            # if this is CapturedFighter without captor boss => reset capture state
            if self.entity_type == EntityType.CAPTURED_FIGHTER and Game.instance.player().get_captor_boss() is None:
                Game.instance.player().captured_fighter = None
                Game.instance.player().capture_state = CaptureState.OFF
        elif self.plan == Plan.DIVE_ATTACK:
            self.plan = Plan.GOTO_GRID
            self.y = 0.0
            self.x = gStartPath[aPath_Top_Double_Right][0]
            if not gMirror[self.position_index]:
                self.x = 100.0 - self.x
        elif self.plan == Plan.GOTO_BEAM:
            self.rotation = 180
            self.sprite.angle = self.rotation
            self.plan = Plan.BEAM_ACTION

    def decision_on_post_path(self):
        # if just launched, set up to shoot, if not a peel-away
        if self.position_index < 44:
            if (self.path_index >> 1) == aPath_Launch:
                self.timer = 0.3
                self.shots_to_fire = 1

        # install the next plan as the plan
        self.plan = self.next_plan

        # Do some setup for the plan that follows completing a path
        if self.plan == Plan.PATH:
            # Set enemy on an arc to face the bottom of the screen
            if self.entity_type == EntityType.BEE:
                self.path_index = PATH_BEE_ATTACK + gMirror[self.position_index]
                self.next_plan = Plan.DESCEND
            else:
                self.path_index = PATH_BUTTERFLY_ATTACK + gMirror[self.position_index]
                self.next_plan = Plan.FLUTTER
            self.next_path_point()
        # After the sweep, get to a height where the circle back starts.
        # Need a seperate state because the bees in rows start at different heights so can't make a path
        # that goes down includes the half-circle arc
        elif self.plan == Plan.DESCEND:
            # Just barely get a wing out the bottom of the screen
            self.delta_dest.x = 0
            self.delta_dest.y = 81.0 - self.y
            self.setup_velocity_and_rotation()
        # after bottom circle, bee must decide to go home or make a full cirlce
        elif self.plan == Plan.HOME_OR_FULL_CIRCLE:
            if Game.instance.player().enemies_alive < 6 and \
                    Game.instance.player().ships[0].plan == Plan.ALIVE:
                self.plan = Plan.PATH
                self.path_index = PATH_BEE_TOP_CIRCLE + 1 - gMirror[self.position_index]
                self.next_path_point()
                # if full circle, afterwards dive out the bottom
                self.next_plan = Plan.DIVE_ATTACK
            else:
                # Half circle was enough, go home
                self.plan = Plan.GOTO_GRID
        # Calculate the flutter arc
        elif self.plan == Plan.FLUTTER:
            self.setup_flutter_arc()
        # Start an attack dive that ends with the enemy disappearing off the bottom
        elif self.plan == Plan.DIVE_AWAY_LAUNCH:
            self.plan = Plan.PATH
            self.next_plan = Plan.DIVE_AWAY
            self.path_index = PATH_LAUNCH + gMirror[self.position_index - 40]
            self.next_path_point()
        # enemy has launched into the dive away, now set the destination and carry on
        # At end, the enemy will simply disappear (die)
        elif self.plan == Plan.DIVE_AWAY:
            # Pick a point to dive at - a 20% range around the player
            left = Game.instance.player().ships[0].x - 10.0
            right = Game.instance.player().ships[0].x + 10.0
            left = utils.clamp(left, 10, 90)
            right = utils.clamp(right, 10, 90)
            self.delta_dest.x = randint(round(left), round(right)) - self.x
            self.delta_dest.y = 103 - self.y
            self.setup_velocity_and_rotation()
        elif self.plan == Plan.DIVE_ATTACK:
            # Send it out the screen
            self.delta_dest.y = 103 - self.y
            self.next_plan = Plan.GOTO_GRID
            self.setup_velocity_and_rotation()
        elif self.plan == Plan.GOTO_BEAM:
            self.delta_dest.x = Game.instance.player().ships[0].x - self.x
            self.delta_dest.y = 62 - self.y
            self.setup_velocity_and_rotation()
        # This is used by the Challange stages
        elif self.plan == Plan.DEAD:
            Game.instance.player().enemies_alive -= 1
            self.sprite.visible = False

    def setup_flutter_arc(self):
        # save the current facing angle
        r = self.rotation - 90
        sign = float(gMirror[self.position_index])

        # Get the angle to the player
        dx = Game.instance.player().ships[0].x - self.x

        # Figure out the flutter pattern (zig/zag/zag)
        if self.y < 65.0:
            dy = 20.0
            if sign == 0:
                dx = utils.clamp(dx, -80, -15)
            else:
                dx = utils.clamp(dx, 15, 80)
        else:
            dy = 15.0
            if sign == 0:
                dx = utils.clamp(dx, 15, 25)
            else:
                dx = utils.clamp(dx, -25, -15)

        # angle to the destination
        self.dr = utils.atan2_deg(dy, dx)
        # rate of turn (increment angle)
        self.ir = (self.dr - r) * 3.0

        # distance to travel (as a line, not on the curve)
        self.delta_dest.x = dx
        self.delta_dest.y = dy
        self.setup_velocity_and_rotation()

        # Restore the sprite angle that was changed in setup_velocity_and_rotation
        r += 90
        self.rotation = r
        self.sprite.angle = self.rotation

    def next_path_point(self):
        index = self.path_index >> 1
        self.delta_dest = glm.vec2(gPathData[index][self.point_index])
        if (self.path_index & 1) != 0:
            self.delta_dest.x = -self.delta_dest.x

        self.setup_velocity_and_rotation()

    def run_beam_action(self):
        sprite = Game.instance.get_first_sprite_by_ent_type(EntityType.BEAM)
        beam_rect = sprite.bounds
        if Game.instance.make_beam == BeamState.POSITION:
            sprite.position = pc2v(glm.vec2(self.x, self.y + 18))
            beam_rect = sprite.bounds
            self.__beam_height = pcy2vy(0.1)
            sprite.scissor = Bounds(beam_rect.left, beam_rect.top, beam_rect.width, self.__beam_height)
            sprite.visible = True
            Game.instance.sfx_play(SOUND_BEAM, -1)
            Game.instance.make_beam += 1
        elif Game.instance.make_beam == BeamState.OPENING:
            self.__beam_height += pcy2vy(BEAM_OPEN_SPEED)
            if self.__beam_height >= beam_rect.height:
                Game.instance.make_beam += 1
                self.__beam_height = beam_rect.height
                self.timer = BEAM_HOLD_DURATION
            sprite.scissor.height = self.__beam_height
        elif Game.instance.make_beam == BeamState.HOLD:
            self.timer -= Game.instance.delta_time
            if self.timer < 0:
                Game.instance.make_beam += 1
        elif Game.instance.make_beam == BeamState.CLOSING:
            self.__beam_height -= pcy2vy(BEAM_OPEN_SPEED)
            if self.__beam_height <= pcy2vy(0.1):
                Game.instance.sfx_stop(SOUND_BEAM)
                sprite.visible = False
                sprite.scissor = None
                Game.instance.make_beam += 1
            else:
                sprite.scissor.height = self.__beam_height
        elif Game.instance.make_beam == BeamState.CLOSED:
            if not Game.instance.player().is_capturing() or Game.instance.player().is_captured():
                if Game.instance.player().is_captured():
                    self.set_captor(True)
                    self.plan = Plan.GOTO_GRID
                    Game.instance.player().captured_fighter.plan = Plan.GOTO_GRID
                    Game.instance.player().captured_fighter.position_index = self.position_index - 4
                else:
                    self.delta_dest.y = 103 - self.y
                    self.plan = Plan.DIVE_ATTACK
                self.setup_velocity_and_rotation()
                Game.instance.make_beam = BeamState.OFF

        # Make the collision box the size of the beam at this stage
        sprite.shape = b2PolygonShape(box=(sprite.size.x / 2.0, self.__beam_height / 2.0))

        if not Game.instance.player().is_capturing() and \
                Game.instance.make_beam >= BeamState.OPENING and \
                Game.instance.player().ships[0].plan != Plan.DEAD and \
                sprite.collide(Game.instance.player().ships[0].sprite):
            Game.instance.sfx_stop(SOUND_BEAM)
            Game.instance.sfx_play(SOUND_BEAM_CAPTURED, -1)
            Game.instance.player().set_captor_boss(self)
            Game.instance.player().capture_state = CaptureState.FIGHTER_TOUCHED

    def was_hit(self) -> bool:
        """
        Enemy.was_hit()

        Check for collision between this enemy and fighter's bullets
        Also check for a possible collision of this enemy with the fighter
        and if so kills the fighter
        """

        player = Game.instance.player()

        # the 1st four are fighter(s) bullets
        for j in range(4):
            bullet = Game.instance.bullets[j]
            if bullet.plan == Plan.ALIVE:
                if self.sprite.collide(bullet.sprite):
                    bullet.plan = Plan.DEAD
                    bullet.sprite.visible = False

                    # Green Commanders become blue, they don't die yet
                    if self.entity_type == EntityType.BOSS_GREEN:
                        # Hide the green
                        self.sprite.visible = False
                        # enable the blue
                        self.entity_type = EntityType.BOSS_BLUE
                        self.sprite = Game.instance.get_first_free_sprite_by_ent_type(EntityType.BOSS_BLUE,
                                                                                      Game.instance.current_player_idx)
                        self.sprite.position = pc2v(glm.vec2(self.x, self.y))
                        self.sprite.angle = self.rotation
                        self.sprite.visible = True
                        Game.instance.sfx_play(SOUND_HIT_COMMANDER_GREEN)
                    else:
                        self.kill()

                    # Don't check other bullets, this enemy is dead
                    return True

        # Check for a collision of this enemy with the player if not in challenge-stage and not spawning
        # during challenge stage or spawn it doesn't collide with the player
        # However during spawn, if this is an extra enemy then check for collision.
        # During spawn, entities with plan == Plan.DIVE_AWAY are extra enemy
        if (player.spawn_active and self.plan != Plan.DIVE_AWAY) or player.stage & 3 == 3:
            return False

        if player.was_hit(self.sprite):
            self.kill()
            return True

        return False

    def kill(self):
        """
        Enemy.kill()
        """

        player = Game.instance.player()
        kind = self.entity_type

        # check if this enemy is a boss, and also is captor
        if kind == EntityType.BOSS_BLUE and self.is_captor():
            player.clear_captor_boss()
            # check that this boss is not sleeping in the grid
            if self.plan != Plan.GRID and self.plan != Plan.ORIENT:
                player.capture_state = CaptureState.RESCUED

        # when destroying captured fighter adjust internal varibles
        if kind == EntityType.CAPTURED_FIGHTER:
            player.capture_state = CaptureState.OFF
            player.captured_fighter = None
            player.clear_captor_boss()

        self.sprite.visible = False

        Game.instance.enemies_killed_this_stage += 1
        player.hits += 1
        player.enemies_alive -= 1

        if self.plan == Plan.BEAM_ACTION:
            Game.instance.get_first_sprite_by_ent_type(EntityType.BEAM).visible = False
            Game.instance.sfx_stop(SOUND_BEAM)
            Game.instance.sfx_stop(SOUND_BEAM_CAPTURED)
            Game.instance.make_beam = BeamState.OFF
            player.ships[0].sprite.angle = 0
            player.capture_state = CaptureState.OFF

        if self.plan == Plan.GRID:
            Game.instance.increment_score(g_score_sheet[kind][0])
        else:
            Game.instance.increment_score(g_score_sheet[kind][1])

        self.plan = Plan.DEAD
        Game.instance.sfx_play(g_kill_sound[self.entity_type])

        if self.attack_index >= 0:
            Game.instance.state.attackers.clear_attacker(self.attack_index)

        # fx_seq = RunningFxSequence()
        effect_explosion = self.create_explosion_fx()
        # effect_score = self.create_score_fx()
        # fx_seq.append(effect_explosion)
        # fx_seq.append(effect_score)
        Game.instance.fx_svc.insert(effect_explosion)

    def create_explosion_fx(self):
        sprite = Game.instance.get_sprite_at_by_ent_type(EntityType.EXPLOSION, Enemy.next_explosion)
        Enemy.next_explosion += 1
        if Enemy.next_explosion == Game.instance.ent_svc.get_sprite_numbers(EntityType.EXPLOSION):
            Enemy.next_explosion = 0
        sprite.position = pc2v(glm.vec2(self.x, self.y))
        sprite.play(restart=True, fps=ENEMY_EXPLOSION_FPS, loop=False)
        frames = Game.instance.ent_svc.get_entity_data(EntityType.EXPLOSION).frame_numbers
        return RunningFx(sprite, frames * (1.0 / (ENEMY_EXPLOSION_FPS + 2)))

    def create_score_fx(self):
        sprite = Game.instance.get_sprite_at_by_ent_type(EntityType.SCORE_800, 0)
        sprite.position = pc2v(glm.vec2(self.x, self.y))
        return RunningFx(sprite, 1.0)

    def fire(self):
        bullet = Game.instance.bullets[Game.instance.bullet_index]
        if bullet.plan == Plan.DEAD:
            player = Game.instance.player()
            bullet.plan = Plan.ALIVE
            bullet.x = self.x
            bullet.y = self.y
            dx = self.x - player.ships[0].x
            dy = self.y - player.ships[0].y

            # Limit the vertical "slide" of the bullets.  This is really
            # tan(angle)*y but tan(45) = 1, so it reduces nicely Clamp(dy#, -dy#, dx#)
            if dx > -dy:
                dx = -dy
            if dx < dy:
                dx = dy

            bullet.distance = math.sqrt(dx * dx + dy * dy)
            r = math.atan2(dy, dx)
            bullet.velocity.x = BULLET_SPEED_ENEMY * math.cos(r)
            bullet.velocity.y = BULLET_SPEED_ENEMY * math.sin(r)

            bullet.delta_dest.x = dx
            bullet.delta_dest.y = dy

            bullet.sprite.position = pc2v(glm.vec2(bullet.x, bullet.y))
            bullet.sprite.visible = True
            Game.instance.bullet_index += 1
            if Game.instance.bullet_index >= MAX_BULLETS:
                Game.instance.bullet_index = Game.instance.ent_svc.get_sprite_numbers(EntityType.BLUE_BULLET)


class CapturedFighter(Enemy):
    def __init__(self):
        super().__init__()
