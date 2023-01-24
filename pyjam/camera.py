from enum import Enum

import glm
import pygame as pg

# default values
FOV = 50  # deg
ZNEAR = 0.1
ZFAR = 100
SPEED = 0.005
SENSITIVITY = 0.04


class ProjectionType(Enum):
    PERSPECTIVE = 0,
    ORTHOGRAPHIC = 1


# all angles must be given in degrees
class Camera:
    def __init__(self, game, eye=glm.vec3(0, 0, 4), yaw=0, pitch=0, roll=0):
        self.__game = game

        # projection params
        self.__aspect = game.get_display_width() / game.get_display_height()
        self.__fovy = FOV  # deg
        self.__znear = ZNEAR
        self.__zfar = ZFAR
        self.__left = -pg.display.get_window_size()[0] / 2.0
        self.__right = pg.display.get_window_size()[0] / 2.0
        self.__bottom = -pg.display.get_window_size()[1] / 2.0
        self.__top = pg.display.get_window_size()[1] / 2.0

        # ---------------------
        # private fields
        # ---------------------

        # view params
        self.__eye = eye
        self.__orientation = glm.quat(glm.vec3(glm.radians(pitch), glm.radians(yaw), glm.radians(roll)))

        # view matrix
        self.__view_matrix = glm.mat4()
        self.__is_view_dirty = True

        # projection matrix
        self.__projection_type = ProjectionType.PERSPECTIVE
        self.__proj_matrix = glm.mat4()
        self.__is_proj_dirty = True

        # allow controlling camera with mouse and keys
        self.__control_enabled = True

        self.update()

    def get_eye(self) -> glm.vec3:
        return self.__eye

    def get_view_matrix(self):
        if self.__is_view_dirty:
            self.update_view()
        return self.__view_matrix

    def get_projection_matrix(self):
        if self.__is_proj_dirty:
            self.update_projection()
        return self.__proj_matrix

    def set_perspective_projection(self, fovy, aspect, znear=ZNEAR, zfar=ZFAR):
        self.__projection_type = ProjectionType.PERSPECTIVE
        self.__fovy = fovy
        self.__aspect = aspect
        self.__znear = znear
        self.__zfar = zfar
        self.__is_proj_dirty = True

    def set_orthographic_projection(self, left, right, bottom, top, znear=ZNEAR, zfar=ZFAR):
        self.__projection_type = ProjectionType.ORTHOGRAPHIC
        self.__left = left
        self.__right = right
        self.__bottom = bottom
        self.__top = top
        self.__znear = znear
        self.__zfar = zfar
        self.__is_proj_dirty = True

    def set_eye(self, eye: glm.vec3):
        self.__eye = glm.vec3(eye)
        self.__is_view_dirty = True

    def translate(self, offset):
        self.__eye += glm.vec3(offset)
        self.__is_view_dirty = True

    def lookat(self, eye: glm.vec3, center: glm.vec3, up: glm.vec3):
        self.__view_matrix = glm.lookAt(eye, center, up)
        pure_rotation_matrix = glm.translate(self.__view_matrix, -eye)
        self.__orientation = glm.quat_cast(pure_rotation_matrix)
        self.__eye = eye
        self.__is_view_dirty = False

    def set_yaw_pitch_roll(self, yaw, pitch, roll):
        self.__orientation = glm.quat(glm.radians(pitch), glm.radians(yaw), glm.radians(roll))
        self.__is_view_dirty = True

    def get_yaw(self):
        return glm.degrees(glm.eulerAngles(self.__orientation).y)

    def get_pitch(self):
        return glm.degrees(glm.eulerAngles(self.__orientation).x)

    def get_roll(self):
        return glm.degrees(glm.eulerAngles(self.__orientation).z)

    def get_forward(self):
        if self.__is_view_dirty:
            self.update_view()

        forward = glm.vec3(self.__view_matrix[0][2], self.__view_matrix[1][2], self.__view_matrix[2][2])
        return glm.normalize(forward)

    def get_right(self):
        if self.__is_view_dirty:
            self.update_view()

        right = glm.vec3(self.__view_matrix[0][0], self.__view_matrix[1][0], self.__view_matrix[2][0])
        return glm.normalize(right)

    def get_up(self):
        m = glm.mat4_cast(self.__orientation)
        return glm.normalize(glm.vec3(m[0]))

    def get_euler_angles(self):
        return glm.degrees(glm.eulerAngles(self.__orientation))

    def update(self):
        if self.__control_enabled:
            self.__move()
            self.__rotate()
            self.__is_view_dirty = True

        if self.__is_view_dirty:
            self.update_view()

        if self.__is_proj_dirty:
            self.update_projection()

    def __move(self):
        velocity = SPEED * self.__game.delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.__eye += self.get_forward() * velocity
        if keys[pg.K_s]:
            self.__eye -= self.get_forward() * velocity
        if keys[pg.K_a]:
            self.__eye -= self.get_right() * velocity
        if keys[pg.K_d]:
            self.__eye += self.get_right() * velocity
        if keys[pg.K_q]:
            self.__eye += self.get_up() * velocity
        if keys[pg.K_e]:
            self.__eye -= self.get_up() * velocity

    def __rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        euler_angles = self.get_euler_angles()
        euler_angles.y += rel_x * SENSITIVITY
        euler_angles.x -= rel_y * SENSITIVITY
        euler_angles.x = max(-89, min(89, int(euler_angles.x)))

    def update_projection(self):
        if self.__projection_type == ProjectionType.PERSPECTIVE:
            self.__proj_matrix = glm.perspective(glm.radians(self.__fovy), self.__aspect, self.__znear, self.__zfar)
        else:
            self.__proj_matrix = glm.ortho(self.__left, self.__right, self.__bottom, self.__top, self.__znear, self.__zfar)
        self.__is_proj_dirty = False

    def update_view(self):
        matrix_rotate = glm.mat4_cast(self.__orientation)
        matrix_translate = glm.translate(glm.mat4(1.0), -self.__eye)
        self.__view_matrix = matrix_translate * matrix_rotate
        self.__is_view_dirty = False
