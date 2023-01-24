# ------------------------------------------------------------------------------
#
# Sprite
#
# ------------------------------------------------------------------------------

import copy

import glm
import pygame as pg
from Box2D import b2PolygonShape, b2Transform, b2Vec2, b2Rot, b2TestOverlap

from pyjam.core import Bounds
from pyjam.sprites import animation
from pyjam.sprites.frame import SpriteFrame
from pyjam.sprites.animation import Animation2D
from pyjam.sprites.batch import SpriteBatch, SpriteEffects
import pyjam.utils as utils


class Sprite:
    def __init__(self, frame: SpriteFrame):
        # sprite hotspot  - x, y
        self.__hotspot = glm.vec2(0, 0)

        # sprite position - x, y
        self.__position = glm.vec2(0, 0)

        # sprite size - width, height
        self.__size = glm.vec2(0, 0)

        # sprite orientation angle in the x,y plane - in degrees
        self.__angle = 0.0

        # sprite scaling factor
        self.__scale = glm.vec2(1, 1)

        # sprite color
        self.__color = pg.Color('white')

        # sprite frame (texture + rect)
        self.__frame = frame

        # current animation
        self.__animation = None

        # whether this sprite updates its animation and physics every frame
        self.__active = True

        # whether this sprite is visible during drawing
        self.__visible = True

        # default sprite layer
        self.__layer_depth = 0.5

        # Box2d shape used for collisions
        self.__shape = None

        self.__scissor = None

        if frame is not None:
            self.size = glm.vec2(frame.rect.w, frame.rect.h)

    @property
    def hotspot(self) -> glm.vec2:
        return self.__hotspot

    @hotspot.setter
    def hotspot(self, hs: glm.vec2):
        self.__hotspot = glm.vec2(hs)

    @property
    def position(self) -> glm.vec2:
        return self.__position

    @position.setter
    def position(self, pos: glm.vec2):
        self.__position = glm.vec2(pos)

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

    def move(self, dx: float = 0.0, dy: float = 0.0):
        self.__position.x += dx
        self.__position.y += dy

    @property
    def width(self) -> float:
        return self.size.x

    @property
    def height(self) -> float:
        return self.size.y

    @property
    def size(self) -> glm.vec2:
        return self.__size

    @size.setter
    def size(self, new_size: glm.vec2):
        self.__size = glm.vec2(new_size)
        self.__hotspot = self.__size / 2
        self.build_shape()

    @property
    def angle(self) -> float:
        return self.__angle

    @angle.setter
    def angle(self, value: float):
        """ Sets the sprite's rotation angle in degrees """

        self.__angle = utils.wrap_angle_deg_180(value)

    @property
    def scale(self) -> glm.vec2:
        return self.__scale

    @scale.setter
    def scale(self, value: glm.vec2):
        """
        Scale the sprite.
        When the sprite is scaled, the hotspot of the sprite is also scaled

        """
        self.__scale = glm.vec2(value)
        self.__hotspot *= self.__scale

    @property
    def color(self) -> pg.Color:
        return self.__color

    @color.setter
    def color(self, value: pg.Color):
        self.__color = pg.Color(value)

    @property
    def frame(self) -> SpriteFrame:
        return self.__frame

    @frame.setter
    def frame(self, value: SpriteFrame):
        self.__frame = value

    @property
    def active(self) -> bool:
        return self.__active

    @active.setter
    def active(self, active_flag: bool):
        self.__active = active_flag

    @property
    def visible(self) -> bool:
        return self.__visible

    @visible.setter
    def visible(self, visible_flag: bool):
        self.__visible = visible_flag

    @property
    def layer_depth(self):
        return self.__layer_depth

    @layer_depth.setter
    def layer_depth(self, ldepth):
        self.__layer_depth = ldepth

    @property
    def shape(self):
        return self.__shape

    @shape.setter
    def shape(self, b2dshape):
        """
        Define the shape used for collision detection.

        In the case of the box shape, it is defined by specifying its top left and bottom right coordinates
        in local (sprite) space, relative to the hotspot of the sprite, by default it is the center of the sprite.
        """
        self.__shape = b2dshape

    @property
    def scissor(self) -> Bounds:
        return self.__scissor

    @scissor.setter
    def scissor(self, value: Bounds):
        self.__scissor = copy.copy(value)

    # set a new animation for the sprite
    def set_animation(self, anim: Animation2D, autostart=True):
        if self.__animation != anim:
            self.__animation = copy.copy(anim)
            if autostart:
                self.__animation.restart()
            self.__frame = self.__animation.get_current_frame()

    def is_playing(self) -> bool:
        return self.__animation is not None and self.__animation.is_playing()

    def play(self, restart=True, fps=animation.DEFAULT_ANIM_FPS, loop=False):
        if self.__animation:
            self.__animation.fps = fps
            self.__animation.enable_loop(loop)
            self.__animation.play(restart)

    def stop(self):
        if self.__animation:
            self.__animation.stop()

    def get_animation(self) -> Animation2D:
        return self.__animation

    def collide(self, sprite) -> bool:
        # TODO should sprite collide if not visible?
        transform_1 = b2Transform(b2Vec2(self.x, self.y), b2Rot(glm.radians(self.angle)))
        transform_2 = b2Transform(b2Vec2(sprite.x, sprite.y), b2Rot(glm.radians(sprite.angle)))
        return b2TestOverlap(self.shape, 0, sprite.shape, 0, transform_1, transform_2)

    def update(self, delta_time: float):
        if self.active:
            if self.is_playing():
                self.__animation.update(delta_time)
                self.__frame = self.__animation.get_current_frame()

    def render(self, sprite_batch: SpriteBatch):
        if self.visible:
            sprite_batch.draw(texture=self.__frame.texture,
                              position=self.__position,
                              source_rect=self.__frame.rect,
                              rotation=self.__angle,
                              color=self.__color,
                              origin=self.__hotspot,
                              scale=self.__scale,
                              size=self.__size,
                              effects=SpriteEffects.NONE,
                              layer_depth=self.__layer_depth,
                              scissor=self.__scissor)

    def build_shape(self):
        self.__shape = b2PolygonShape(
            box=(self.__size.x / 2, self.__size.y / 2, (0, 0), glm.radians(self.__angle)))

    @property
    def bounds(self) -> Bounds:
        # TODO handle sprite scale
        return Bounds(self.x-self.hotspot.x, self.y-self.hotspot.y,
                      self.size.x * self.scale.x, self.size.y * self.scale.y)
