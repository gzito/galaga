from pyjam.sprite import Sprite


class RunningFx:
    def __init__(self, spr: Sprite, ttl: float):
        self.__ttl = ttl
        self.__spr = spr
        self.__entered = False
        self.__exited = False

    @property
    def time_to_live(self):
        return self.__ttl

    @property
    def sprite(self):
        return self.__spr

    def update(self, delta_time):
        if not self.__entered:
            self.enter_action()
        self.__ttl -= delta_time
        if self.__ttl < 0:
            self.exit_action()

    def enter_action(self):
        self.__spr.visible = True
        self.__entered = True

    def exit_action(self):
        self.__spr.visible = False
        self.__exited = True

    def is_done(self):
        return self.__exited is True


class RunningFxSequence:
    def __init__(self):
        self.__running_fx = []
        self.__idx = 0

    def append(self, running_fx):
        self.__running_fx.append(running_fx)

    def update(self, delta_time):
        if self.__idx < len(self.__running_fx):
            self.__running_fx[self.__idx].update(delta_time)
            if self.__running_fx[self.__idx].is_done():
                self.__idx += 1

    def is_done(self):
        return self.__idx >= len(self.__running_fx)


class RunningFxService:
    def __init__(self, game):
        self.__fx_list = []
        self.__game = game

    def insert(self, fx):
        self.__fx_list.append(fx)

    def remove(self, idx):
        self.__fx_list.pop(idx)

    def update(self, delta_time):
        done_list = []
        for idx, fx in enumerate(self.__fx_list):
            fx.update(delta_time)
            if fx.is_done():
                done_list.append(idx)

        done_list.sort(reverse=True)
        for idx in done_list:
            self.remove(idx)

    @property
    def effects(self):
        return self.__fx_list
