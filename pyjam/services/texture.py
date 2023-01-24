import os

import moderngl as mgl
import pygame as pg
import PIL.Image
import PIL.ImageOps

from pyjam.interfaces import IDisposable
from pyjam.sprites.frame import SpriteFrame
from pyjam.texture import Texture2D
from pyjam.constants import *


class TextureService(IDisposable):
    def __init__(self, game):
        super().__init__()
        self.__game = game
        self.__texture2d_list = []

    def load_sprite_frame(self, path: str) -> SpriteFrame:
        sprite_frame = SpriteFrame(self.load_texture(path))
        self.__game.services[ASSET_SERVICE].insert(path, sprite_frame)
        return sprite_frame

    def load_texture(self, path: str) -> Texture2D:
        asset_root = self.__game.get_assets_root()

        fname = os.path.join(asset_root, path)
        print(f'Loading file: {fname}')
        img = PIL.ImageOps.flip(PIL.Image.open(fname))
        rgba_img = img.convert('RGBA')

        # handle BMFont luminance textures
        if img.mode == 'L':
            channels = rgba_img.split()
            channels[3].paste(img)
            rgba_img = PIL.Image.merge('RGBA', channels)

        texture2d = self._from_pillow_image(rgba_img)
        self.__texture2d_list.append(texture2d)

        #surface = pg.image.load(path)
        #rgba_surface = surface.convert_alpha()
        #texture2d = self._from_pg_surface(rgba_surface, path)

        return texture2d

    def create_color_texture(self, color: pg.Color) -> Texture2D:
        surface = pg.Surface((1, 1), pg.SRCALPHA)
        surface.fill(color)
        texture2d = self._from_pg_surface(surface)
        return texture2d

    def _from_pillow_image(self, img) -> Texture2D:
        components = len(img.getbands())
        mgltex = self.__game.ctx.texture(size=img.size, components=components,
                                         data=img.tobytes())

        return TextureService._setup_texture(mgltex)

    def _from_pg_surface(self, surface: pg.Surface) -> Texture2D:
        flipped_surface = pg.transform.flip(surface, flip_x=False, flip_y=True)
        mgltex = self.__game.ctx.texture(size=flipped_surface.get_size(), components=4,
                                         data=pg.image.tostring(flipped_surface, 'RGBA'))
        return TextureService._setup_texture(mgltex)

    @staticmethod
    def _setup_texture(mgltex) -> Texture2D:
        # mipmaps
        mgltex.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        mgltex.build_mipmaps(max_level=10)

        # Disable anisotropic Filtering
        mgltex.anisotropy = 16.0

        return Texture2D(mgltex)

    def dispose(self):
        [texture2d.dispose() for texture2d in self.__texture2d_list]

