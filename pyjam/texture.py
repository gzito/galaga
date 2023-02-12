# a tiny wrapper around mlg texture

import moderngl as mgl

from pyjam.interfaces import IDisposable


class Texture2D(IDisposable):
    __last_sorting_key = 0

    def __init__(self, mgltex: mgl.Texture):
        self.__mgltex = mgltex
        Texture2D.__last_sorting_key += 1
        self.__sorting_key = Texture2D.__last_sorting_key

    def dispose(self):
        self.__mgltex.release()

    @property
    def width(self):
        return self.__mgltex.width

    @property
    def height(self):
        return self.__mgltex.height

    @property
    def mgl_texture(self):
        return self.__mgltex

    @property
    def sorting_key(self):
        return self.__sorting_key


