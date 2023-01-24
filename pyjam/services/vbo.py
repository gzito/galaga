import numpy as np

from pyjam.interfaces import IDisposable


class VboService(IDisposable):
    def __init__(self, game):
        self.__game = game
        self.vbos = {'quad': QuadVBO(self.__game.ctx),
                     'line': LineVBO(self.__game.ctx)}

    def dispose(self):
        [vbo.dispose() for vbo in self.vbos.values()]


class BaseVBO(IDisposable):
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.ebo = self.get_ebo()
        self.format: str = ''
        self.attribs: list = []

    def get_vbo(self):
        return self.ctx.buffer(self.get_vertices_data())

    def get_ebo(self):
        return self.ctx.buffer(self.get_indices_data())

    def get_vertices_data(self):
        pass

    def get_indices_data(self):
        pass

    def dispose(self):
        self.vbo.release()
        self.ebo.release()


class QuadVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 4f1 2f'
        self.attribs = ['in_position', 'in_color', 'in_tex_coords_0']

    def get_vertices_data(self):
        vertices = [(-25.0, -25.0, 0.0, 0xffffffff, 0.0, 0.0),
                    (25.0, -25.0, 0.0, 0xffffffff, 1.0, 0.0),
                    (-25.0, 25.0, 0.0, 0xffffffff, 0.0, 1.0),
                    (25.0, 25.0, 0.0, 0xffffffff, 1.0, 1.0)]
        ndarr = np.array(vertices, dtype='f4, f4, f4, u4, f4, f4')
        return ndarr

    def get_indices_data(self):
        indices = [0, 1, 2, 1, 3, 2]
        return np.array(indices, dtype='i2')


class LineVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 4f1'
        self.attribs = ['in_position', 'in_color']

    def get_vertices_data(self):
        vertices = [(0.0, 0.0, 0.0, 0xffffffff),
                    (1.0, 1.0, 0.0, 0xffffffff)]
        ndarr = np.array(vertices, dtype='f4, f4, f4, u4')
        return ndarr

    def get_indices_data(self):
        indices = [0, 1]
        return np.array(indices, dtype='i2')
