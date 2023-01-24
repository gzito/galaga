import moderngl as mgl
import pyjam
from pyjam.interfaces import IDisposable
from pyjam.constants import *


class ShaderService(IDisposable):
    def __init__(self, game: 'pyjam.application.Game', shader_folder: str = ''):
        self.__game = game
        self.programs = {SHADER_DEFAULT_SPRITES: self.get_program(shader_folder, SHADER_DEFAULT_SPRITES),
                         SHADER_UNTEXTURED: self.get_program(shader_folder, SHADER_UNTEXTURED)}

    def get_program(self, shader_folder: str, shader_name: str) -> mgl.program:
        if shader_folder == '':
            shader_folder = pyjam.get_data('shaders')

        with open(f'{shader_folder}/{shader_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'{shader_folder}/{shader_name}.frag') as file:
            fragment_shader = file.read()

        return self.__game.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def dispose(self):
        [program.release() for program in self.programs.values()]
