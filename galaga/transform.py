class TransformData:
    def __init__(self, src_enemy_kind, dst_enemy_kind):
        # original enemy (bee or butterfly)
        self.src_enemy_kind = src_enemy_kind
        self.src_sprite = None

        # transformed enemy: scorpion, bosconian or galaxian
        self.dst_enemy_kind = dst_enemy_kind


class TransformService:
    def __init__(self):
        # the list of 3 transforms
        self.__transforms = [-1, -1, -1]
        self.__transforms_num = 0

    def get_transform(self, idx):
        return self.__transforms[idx]

    @property
    def transforms_count(self):
        return self.__transforms_num

    def set(self, idx, transform_grid_position):
        self.__transforms[idx] = transform_grid_position

    def append(self, transform_grid_position):
        self.__transforms[self.__transforms_num] = transform_grid_position
        self.__transforms_num += 1

    def remove(self, transform_grid_position):
        for i in range(3):
            if self.__transforms[i] == transform_grid_position:
                self.__transforms[i] = -1
                self.__transforms_num -= 1
                break

    def is_active(self):
        return self.__transforms_num > 0

    def reset(self):
        for i in range(3):
            self.__transforms[i] = -1
        self.__transforms_num = 0
