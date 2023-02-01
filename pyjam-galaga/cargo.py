from pyjam.application import Game


class Cargo:
    @property
    def game(self):
        return Game.instance

    # only used by bosses
    # the cargo items are the index positions of cargo-entity in the grid
    # max 3 cargo, included captured fighter which will be the last item of 3

    def __init__(self):
        self.__cargo = [-1, -1, -1]
        self.__num_cargo = 0

    def count(self):
        return self.__num_cargo

    def clear_all(self):
        for i in range(len(self.__cargo)):
            self.clear_at(i)
        self.__num_cargo = 0

    def get_at(self, idx):
        return self.__cargo[idx]

    def insert_from(self, from_idx, position_in_the_grid):
        """ add a cargo at the first available slot starting from the index from_idx """
        for i in range(from_idx, len(self.__cargo)):
            if self.__cargo[i] == -1:
                self.__cargo[i] = position_in_the_grid
                self.game.enemy_at(position_in_the_grid).cargo_index = i
                self.__num_cargo += 1
                break

    def clear_at(self, idx):
        """ delete the cargo with the given index from cargo slots """
        if self.__cargo[idx] != -1:
            self.__cargo[idx] = -1
            self.__num_cargo -= 1
