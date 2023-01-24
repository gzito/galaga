from pyjam.interfaces import IDisposable
from pyjam.constants import *


class VaoService(IDisposable):
    def __init__(self, game):
        self.__game = game
        self.vaos = {
            'quad': self.get_vao(
                program=self.__game.services[SHADER_SERVICE].programs[SHADER_DEFAULT_SPRITES],
                vbo=self.__game.services[VBO_SERVICE].vbos['quad']),
            'line': self.get_vao(
                program=self.__game.services[SHADER_SERVICE].programs[SHADER_UNTEXTURED],
                vbo=self.__game.services[VBO_SERVICE].vbos['line'])}

    def get_vao(self, program, vbo):
        vao = self.__game.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)],
                                           index_buffer=vbo.ebo,
                                           index_element_size=2, skip_errors=True)
        return vao

    def dispose(self):
        [vao.release() for vao in self.vaos.values()]
