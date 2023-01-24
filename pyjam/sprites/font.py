import os
import xml.etree.ElementTree as ET

import glm

from pyjam.constants import *


class Glyphs:
    def __init__(self):
        # The character id
        self.id = 0
        # The left position of the character image in the texture
        self.x = 0
        # The top position of the character image in the texture
        self.y = 0
        # The width of the character image in the texture
        self.width = 0
        # The height of the character image in the texture
        self.height = 0
        # How much the current position should be offset when copying the image from the texture to the screen
        self.xoffset = 0
        # How much the current position should be offset when copying the image from the texture to the screen
        self.yoffset = 0
        # How much the current position should be advanced after drawing the character
        self.xadvance = 0
        # The texture page where the character image is found
        self.page = 0


#
# https://www.angelcode.com/products/bmfont/doc/file_format.html
#
class SpriteFont:
    def __init__(self, game):
        # The size of the true type font
        self.size = 0
        # The distance in pixels between each line of text
        self.line_height = 0
        # The number of pixels from the absolute top of the line to the base of the characters
        self.base = 0
        # The spacing for each character (horizontal, vertical)
        self.spacing = 0
        # The number of texture pages included in the font
        self.pages = 0

        self.glyphs = {}
        self.sprite_frame_list = []
        self.game = game

    def load(self, filename: str):
        asset_root = self.game.get_assets_root()
        tree = ET.parse(os.path.join(asset_root, filename))
        font_elem = tree.getroot()
        info_elem = font_elem.find('info')
        self.size = int(info_elem.attrib['size'])
        spacing = info_elem.attrib['spacing']
        self.spacing = int(spacing.split(',')[0])
        common_elem = font_elem.find('common')
        self.line_height = int(common_elem.attrib['lineHeight'])
        self.base = int(common_elem.attrib['base'])
        self.pages = int(common_elem.attrib['pages'])
        pages_elem = font_elem.find('pages')
        for page in pages_elem.findall('page'):
            # page_id = int(page.attrib['id'])
            page_file = page.attrib['file']
            texture_service = self.game.services[TEXTURE_SERVICE]
            texture_path = os.path.join(os.path.dirname(filename), page_file)
            sprite_frame = texture_service.load_sprite_frame(texture_path)
            self.sprite_frame_list.append(sprite_frame)

        chars_elem = font_elem.find('chars')
        for char in chars_elem.findall('char'):
            g = Glyphs()
            g.id = int(char.attrib['id'])
            g.x = int(char.attrib['x'])
            g.y = int(char.attrib['y'])
            g.width = int(char.attrib['width'])
            g.height = int(char.attrib['height'])
            g.xoffset = int(char.attrib['xoffset'])
            g.yoffset = int(char.attrib['yoffset'])
            g.xadvance = int(char.attrib['xadvance'])
            g.page = int(char.attrib['page'])
            self.glyphs[g.id] = g

        self.game.services[ASSET_SERVICE].insert(filename, self)

    def measure_string(self, text: str):
        if text == '':
            return glm.vec2(0)

        final_line_height = float(self.line_height)
        offset = glm.vec2(0)
        first_glyph_of_line = True

        for i in range(len(text)):
            c = text[i]

            if c == '\r':
                continue

            if c == '\n':
                final_line_height = float(self.line_height)
                offset.x = 0
                offset.y += final_line_height
                continue

            current_glyph = self.glyphs[c]

            # The first character on a line might have a negative left side bearing.
            # In this scenario, SpriteBatch/SpriteFont normally offset the text to the right,
            # so that text does not hang off the left side of its rectangle.
            if first_glyph_of_line:
                offset.x = 0
                first_glyph_of_line = False

            if i != len(text)-1:
                offset.x += current_glyph.xadvance
            else:
                offset.x += current_glyph.width

            if current_glyph.height > final_line_height:
                final_line_height = current_glyph.height

        return glm.vec2(offset.x, offset.y+final_line_height)
