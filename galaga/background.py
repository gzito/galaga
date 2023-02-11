from constants import *
from pyjam.sprite import Sprite
from pyjam.application import *
from pyjam.constants import *


class Star(Sprite):
    def __init__(self, service, frame):
        super().__init__(frame)

        self.__service = service

        self.time_to_live = random.randint(200, 400) / 1000.0
        self.counter = self.time_to_live

        self.layer_depth = 1.0
        self.size = pc2v(glm.vec2(STAR_WIDTH, STAR_HEIGHT))
        self.color = pg.Color(random.randint(20, 255), random.randint(20, 255), random.randint(20, 255), 255)
        self.position = pc2v(glm.vec2(random.randint(0, 100), 5 + random.randint(0, 89)))
        self.visible = True if random.randint(0, 1) == 1 else False

    @property
    def speed(self):
        return self.__service.speed

    def update(self, delta_time: float):
        if self.active:
            dygdt = pcy2vy(self.speed) * delta_time
            self.counter -= delta_time
            if self.counter < 0:
                self.visible = not self.visible
                self.counter = self.time_to_live

            sy = self.y + dygdt
            if sy > pcy2vy(94):
                sy -= pcy2vy(89)
            elif sy < pcy2vy(6):
                sy += pcy2vy(89)
            self.y = sy


class StarsService:
    def __init__(self, game):
        self.__stars_speed = 0.0
        self.__game = game
        self.__stars = []

    @property
    def speed(self) -> float:
        return self.__stars_speed

    @speed.setter
    def speed(self, new_speed: float):
        self.__stars_speed = new_speed

    def create_stars(self, count: int):
        while count:
            a_star = Star(self, self.__game.services[ASSET_SERVICE].get('textures/star'))
            a_star.layer_depth = 1.0
            self.__game.sprites.append(a_star)
            self.__stars.append(a_star)
            count -= 1

    def enable(self):
        for s in self.__stars:
            s.active = True

    def disable(self):
        for s in self.__stars:
            s.active = False
