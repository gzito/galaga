import pygame as pg


# a simple pair of Texture2D and Rect, used to represent square region of a texture atlas
class SpriteFrame:
    def __init__(self, texture, rect=None):
        self.texture = texture
        if rect is None:
            self.rect = pg.Rect((0, 0), (texture.width, texture.height))
        else:
            self.rect = rect

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
