import glm

from pyjam import utils
from pyjam.sprites.batch import SpriteBatch
from pyjam.texture import Texture2D


def draw_line(sprite_batch: SpriteBatch, x1: float, y1: float, x2: float, y2: float,
              texture: Texture2D, thickness: float):
    point_1 = glm.vec2(x1, y1)
    point_2 = glm.vec2(x2, y2)

    distance = glm.distance(point_1, point_2)
    angle = utils.atan2_deg(y2-y1, x2-x2)

    sprite_batch.draw(texture=texture, position=point_1, rotation=angle,
                      scale=glm.vec2(distance, thickness), layer_depth=0.2)
