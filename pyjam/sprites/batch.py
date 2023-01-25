import math
from enum import IntEnum

import glm
import moderngl as mgl
import numpy as np
import pygame as pg

from pyjam import utils
from pyjam.constants import *
from pyjam.core import Bounds
from pyjam.interfaces import IDisposable
from pyjam.sprites.sheet import SpriteSheet
from pyjam.texture import Texture2D


class SpriteEffects(IntEnum):
    NONE = 0,
    FLIP_HORIZONTALLY = 1,
    FLIP_VERTICALLY = 2


class SpriteSortMode(IntEnum):
    # Sprites are not drawn until End is called. End will apply graphics device settings
    # and draw all the sprites in one batch, in the same order calls to Draw were received.
    DEFERRED = 0,

    # Begin will apply new graphics device settings, and sprites will be drawn within each Draw call.
    IMMEDIATE = 1,

    # Same as Deferred mode, except sprites are sorted by texture prior to drawing. Depth is ignored.
    TEXTURE = 2,

    # Same as Deferred mode, except sprites are sorted by depth in back-to-front order prior to drawing.
    # This procedure is recommended when drawing transparent sprites of varying depths.
    # If you use BACK_TO_FRONT sorting mode sprites are sorted by -layer_depth, so that the higher number layers
    # will be drawn first
    BACK_TO_FRONT = 3,

    # Same as Deferred mode, except sprites are sorted by depth in front-to-back order prior to drawing.
    # This procedure is recommended when drawing opaque sprites of varying depths.
    # If you use FRONT_TO_BACK sorting mode sprites are sorted by +layer_depth, so that the lower number layers
    # will be drawn first
    FRONT_TO_BACK = 4


class SpriteBatchItem:
    def __init__(self):
        self.texture = None
        self.sortkey = 0.0
        self.vertexTL = ()
        self.vertexTR = ()
        self.vertexBL = ()
        self.vertexBR = ()

    def set(self, x, y, w, h, color: pg.Color, tex_coord_tl: glm.vec2, tex_coord_br: glm.vec2, depth):
        rgba = utils.swap_endians(int(color))

        self.vertexTL = (x, y + h, depth, rgba, tex_coord_tl.x, tex_coord_tl.y)
        self.vertexTR = (x + w, y + h, depth, rgba, tex_coord_br.x, tex_coord_tl.y)
        self.vertexBL = (x, y, depth, rgba, tex_coord_tl.x, tex_coord_br.y)
        self.vertexBR = (x + w, y, depth, rgba, tex_coord_br.x, tex_coord_br.y)

    def set_extended(self, x, y, dx, dy, w, h, sin, cos, color: pg.Color, tex_coord_tl: glm.vec2,
                     tex_coord_br: glm.vec2, depth):
        rgba = utils.swap_endians(int(color))

        # rotation around origin (x0,y0)
        # x1 = x0cos(a) - y0sin(a)
        # y1 = x0sin(a) + y0cos(a)

        self.vertexTL = (
            x + dx * cos - (dy + h) * sin, y + dx * sin + (dy + h) * cos, depth, rgba, tex_coord_tl.x, tex_coord_tl.y)
        self.vertexTR = (
            x + (dx + w) * cos - (dy + h) * sin, y + (dx + w) * sin + (dy + h) * cos, depth, rgba, tex_coord_br.x,
            tex_coord_tl.y)
        self.vertexBL = (
            x + dx * cos - dy * sin, y + dx * sin + dy * cos, depth, rgba, tex_coord_tl.x,
            tex_coord_br.y)
        self.vertexBR = (
            x + (dx + w) * cos - dy * sin, y + (dx + w) * sin + dy * cos, depth, rgba, tex_coord_br.x,
            tex_coord_br.y)


class SpriteBatcher(IDisposable):
    def __init__(self, game, capacity=0):
        self.__initial_batch_size = 256

        # limit enforced by indices size (16 bit)
        # there are 6 indices per batch item
        self.__max_batch_size = int(65536 / 6)

        self.__batch_item_count = 0
        self.__batch_item_list = []

        self.__index_list = []
        self.__vertex_list = []

        self.__program = game.services[SHADER_SERVICE].programs[SHADER_DEFAULT_SPRITES]

        # self.__texture = None

        self.__ctx = game.ctx
        self.__vbo = None
        self.__ebo = None
        self.__vao = None

        self.__uploaded = False

        if capacity <= 0:
            capacity = self.__initial_batch_size
        else:
            # capacity = round(capacity + 63) & (~63)  # ensure chunks of 64
            capacity = 1

        self.ensure_array_capacity(capacity)

    def create_batch_item(self):
        if self.__batch_item_count >= len(self.__batch_item_list):
            old_size = len(self.__batch_item_list)
            new_size = round(old_size + (old_size / 2))  # grow by x1.5
            new_size = (new_size + 63) & (~63)  # grow in chunks of 64
            self.ensure_array_capacity(min(new_size, self.__max_batch_size))
            self.__batch_item_list.append(SpriteBatchItem())

        item = self.__batch_item_list[self.__batch_item_count]
        self.__batch_item_count += 1
        return item

    def draw_batch(self, sort_mode):
        if self.__batch_item_count == 0:
            return

        if sort_mode == SpriteSortMode.TEXTURE or\
                sort_mode == SpriteSortMode.FRONT_TO_BACK or \
                sort_mode == SpriteSortMode.BACK_TO_FRONT:
            # sort the list
            # warning: do not sort the entire list in place, only the relevant portion have to be sorted
            self.__batch_item_list[0:self.__batch_item_count] = \
                sorted(self.__batch_item_list[0:self.__batch_item_count], key=lambda it: it.sortkey)

        batch_count = self.__batch_item_count
        while batch_count > 0:
            start_vertex = 0
            end_vertex = 0
            tex = None

            num_batches_to_process = batch_count
            if num_batches_to_process > self.__max_batch_size:
                num_batches_to_process = self.__max_batch_size

            vlist_idx = 0

            for i in range(num_batches_to_process):
                item = self.__batch_item_list[i]

                # if the texture changed (or the first time), we need to flush and bind the new texture
                if tex is not item.texture:
                    # the first time start_index == index, so flush() does nothing
                    self.flush_vertex_array(start_vertex, end_vertex)

                    start_vertex = end_vertex = 0
                    vlist_idx = 0

                    tex = item.texture
                    self.__program['material_diffuse'] = 0
                    tex.mgl_texture.use(location=0)

                self.__vertex_list[vlist_idx + 0] = item.vertexTL
                self.__vertex_list[vlist_idx + 1] = item.vertexTR
                self.__vertex_list[vlist_idx + 2] = item.vertexBL
                self.__vertex_list[vlist_idx + 3] = item.vertexBR

                end_vertex += 4
                vlist_idx += 4

            self.flush_vertex_array(start_vertex, end_vertex)
            batch_count -= num_batches_to_process

        self.__batch_item_count = 0

    def upload_vertex_buffer(self):
        if self.__uploaded:
            return

        ndarr = np.array(self.__vertex_list, dtype='f4, f4, f4, u4, f4, f4')
        self.__vbo = self.__ctx.buffer(ndarr, dynamic=True)
        self.__ebo = self.__ctx.buffer(np.array(self.__index_list, dtype='i2'))

        fmt = '3f 4f1 2f'
        attribs = ['in_position', 'in_color', 'in_tex_coords_0']
        self.__vao = self.__ctx.vertex_array(self.__program, [(self.__vbo, fmt, *attribs)],
                                             index_buffer=self.__ebo, index_element_size=2, skip_errors=True)
        self.__uploaded = True

    def update_vertex_buffer(self, start, end):
        sizeof_vertex_in_bytes = 24  # (3 * 4) + 4 + (2 * 4)
        vertex_l = self.__vertex_list[start:end]
        ndarr = np.array(vertex_l, dtype='f4, f4, f4, u4, f4, f4')
        self.__vbo.write(ndarr, offset=start * sizeof_vertex_in_bytes)

    def flush_vertex_array(self, start, end):
        if start == end:
            return

        if not self.__uploaded:
            self.upload_vertex_buffer()
        else:
            self.update_vertex_buffer(start, end)

        vertex_count = int((end - start) * 1.5)
        self.__vao.render(vertices=vertex_count, first=start)

    def ensure_array_capacity(self, needed_batch_items):
        needed_capacity = 6 * needed_batch_items
        if len(self.__index_list) > 0 and needed_capacity <= len(self.__index_list):
            # Short circuit out of here because we have enough capacity.
            return

        num_batches = 0
        if len(self.__index_list) > 0:
            num_batches = len(self.__index_list) / 6

        while num_batches < needed_batch_items:
            #
            #  TL    TR
            #   0----1 0,1,2,3 = index offsets for vertex indices
            #   |   /| TL,TR,BL,BR are vertex references in SpriteBatchItem.
            #   |  / | front-face is 'ccw'
            #   | /  | y is positive down the screen
            #   |/   |
            #   2----3
            #  BL    BR
            #
            self.__index_list.append(num_batches * 4 + 0)
            self.__index_list.append(num_batches * 4 + 1)
            self.__index_list.append(num_batches * 4 + 2)

            self.__index_list.append(num_batches * 4 + 1)
            self.__index_list.append(num_batches * 4 + 3)
            self.__index_list.append(num_batches * 4 + 2)

            for x in range(4):
                self.__vertex_list.append(tuple((0.0, 0.0, 0.0, 0, 0.0, 0.0)))

            num_batches += 1

        if self.__uploaded:
            self.dispose()

    def dispose(self):
        if self.__vao is not None:
            self.__vao.release()
        if self.__ebo is not None:
            self.__ebo.release()
        if self.__vbo is not None:
            self.__vbo.release()
        self.__uploaded = False


class SpriteBatch(IDisposable):
    def __init__(self, game, capacity=0):
        self.__sort_mode = SpriteSortMode.DEFERRED
        self.__batcher = SpriteBatcher(game, capacity)
        self.__begin_called = False
        self.__tex_coord_tl = glm.vec2()
        self.__tex_coord_br = glm.vec2()
        self.__transform_matrix = glm.identity(glm.mat4)
        self.__scissor = None
        self.blend_equation = mgl.FUNC_ADD
        self.blend_func = mgl.DEFAULT_BLENDING
        self.depth_test_enabled = False
        self.__game = game

    def setup(self):
        # blend stuff here
        self.__game.ctx.enable(mgl.BLEND)
        self.__game.ctx.blend_equation = self.blend_equation
        self.__game.ctx.blend_func = self.blend_func
        if self.depth_test_enabled:
            self.__game.ctx.enable(mgl.DEPTH_TEST)
        else:
            self.__game.ctx.disable(mgl.DEPTH_TEST)

        program = self.__game.services[SHADER_SERVICE].programs[SHADER_DEFAULT_SPRITES]
        program['proj_matrix'].write(self.__game.camera.get_projection_matrix())
        program['view_matrix'].write(self.__game.camera.get_view_matrix())
        program['model_matrix'].write(self.__transform_matrix)
        program['material_diffuse'] = 0

    def cleanup(self):
        self.__game.ctx.disable(mgl.BLEND)
        self.__game.ctx.enable(mgl.DEPTH_TEST)
        self.unset_scissor()

    def unset_scissor(self):
        if self.__scissor is not None:
            self.__scissor = None
            self.__game.ctx.scissor = None

    def set_scissor(self, scissor: Bounds):
        self.__scissor = scissor
        v1 = glm.vec3(self.__scissor.left, self.__scissor.top, 0)
        v2 = glm.vec3(self.__scissor.left + self.__scissor.width, self.__scissor.top + self.__scissor.height, 0)

        v1.y, v2.y = v2.y, v1.y

        clip_v1 = glm.round(self.__game.world_to_screen(v1))
        clip_v2 = glm.round(self.__game.world_to_screen(v2))

        w = clip_v2.x - clip_v1.x
        h = abs(clip_v2.y - clip_v1.y)

        # ModernGL scissor: the first 2 coordinates define the lower-left corner;
        # the other 2 coordinates define the width and height of box
        self.__game.ctx.scissor = clip_v1.x, clip_v1.y, w, h

    def check_valid(self, texture):
        if texture is None:
            raise Exception('Argument None: texture')
        if not self.__begin_called:
            raise Exception(
                'Draw was called, but Begin has not yet been called. Begin must be called successfully before you can '
                'call Draw.')

    def flush(self):
        self.__batcher.draw_batch(self.__sort_mode)

    def flush_if_needed(self):
        if self.__sort_mode == SpriteSortMode.IMMEDIATE:
            self.__batcher.draw_batch(self.__sort_mode)

    #
    # Default blend_func is ALPHA_BLEND -> SRC_ALPHA, ONE_MINUS_SRC_ALPHA
    #
    # When calling drawing commands, layer_depth must be in the range [0.0, 1.0]
    # 0.0 means nearest to the observer
    # 1.0 means farthest from the observer
    # layer_depth is only considered when using sorting modes back-to-front or front-to-back
    #
    def begin(self, sort_mode=SpriteSortMode.DEFERRED,
              blend_func=mgl.DEFAULT_BLENDING,
              blend_equation=mgl.FUNC_ADD,
              depth_test_enabled=False,
              transform_matrix=glm.identity(glm.mat4)):
        if self.__begin_called:
            raise Exception('Begin cannot be called again until End has been successfully called.')

        self.blend_func = blend_func
        self.blend_equation = blend_equation
        self.depth_test_enabled = depth_test_enabled
        self.__sort_mode = sort_mode

        if self.__sort_mode == SpriteSortMode.IMMEDIATE:
            self.setup()

        self.__transform_matrix = transform_matrix

        self.__begin_called = True

    def end(self):
        if not self.__begin_called:
            raise Exception('Begin must be called before calling End.')

        self.__begin_called = False
        if self.__sort_mode != SpriteSortMode.IMMEDIATE:
            self.setup()

        self.flush()
        self.cleanup()

    def draw(self,
             texture: Texture2D,
             position: glm.vec2,
             source_rect: pg.Rect = None,
             rotation: float = 0.0,
             color: pg.Color = pg.Color('white'),
             origin: glm.vec2 = glm.vec2(0.0, 0.0),
             scale: glm.vec2 = glm.vec2(1.0, 1.0),
             size: glm.vec2 = None,
             effects: SpriteEffects = SpriteEffects.NONE,
             layer_depth: float = 0,
             scissor: Bounds = None):

        self.check_valid(texture)

        if scissor:
            self.setup()
            self.flush()
            self.set_scissor(scissor)

        item = self.__batcher.create_batch_item()
        item.texture = texture
        if self.__sort_mode == SpriteSortMode.TEXTURE:
            item.sortkey = texture.sorting_key
        elif self.__sort_mode == SpriteSortMode.FRONT_TO_BACK:
            item.sortkey = layer_depth
        elif self.__sort_mode == SpriteSortMode.BACK_TO_FRONT:
            item.sortkey = -layer_depth

        s = scale

        # sprite size
        if size is not None:
            w = size.x * s.x
            h = size.y * s.y
        elif source_rect is not None:
            w = source_rect.width * s.x
            h = source_rect.height * s.y
        else:
            w = texture.width * s.x
            h = texture.height * s.y

        # the hotspot is scaled with sprite, so we don't scale again here
        # scaled_origin = origin * s

        # texture coordinates
        if source_rect is not None:
            texel_width = 1.0 / texture.width
            texel_height = 1.0 / texture.height
            self.__tex_coord_tl = glm.vec2(source_rect.left * texel_width, 1.0 - (source_rect.top * texel_height))
            self.__tex_coord_br = glm.vec2((source_rect.left + source_rect.w) * texel_width,
                                           1.0 - ((source_rect.top + source_rect.h) * texel_height))
        else:
            self.__tex_coord_tl = glm.vec2(0, 1)
            self.__tex_coord_br = glm.vec2(1, 0)

        if self.__game.is_origin_topleft():
            self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

        if effects & SpriteEffects.FLIP_VERTICALLY:
            self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

        if effects & SpriteEffects.FLIP_HORIZONTALLY:
            self.__tex_coord_tl.x, self.__tex_coord_br.x = self.__tex_coord_br.x, self.__tex_coord_tl.x

        if rotation == 0:
            item.set(position.x - origin.x, position.y - origin.y,
                     w, h,
                     color,
                     self.__tex_coord_tl, self.__tex_coord_br,
                     layer_depth)
        else:
            item.set_extended(position.x, position.y,
                              -origin.x, -origin.y,
                              w, h,
                              utils.sin_deg(rotation), utils.cos_deg(rotation),
                              color,
                              self.__tex_coord_tl, self.__tex_coord_br,
                              layer_depth)

        # We need to flush if we're using Immediate sort mode.
        if scissor:
            self.flush()
            self.unset_scissor()
        else:
            self.flush_if_needed()

    def draw_string(self, sp_sheet: SpriteSheet, text: str, position: glm.vec2,
                    w: float, h: float, rotation: float,
                    chars_colors=None, kerning_width=0, layer_depth: float = 0.1):
        if chars_colors is None:
            chars_colors = list()
            for i in range(len(text)):
                chars_colors.append(pg.Color('white'))
                
        offset = glm.ivec2(0, 0)
        first_char_of_line = True

        texture = sp_sheet.texture2d

        sort_key = 0.0
        if self.__sort_mode == SpriteSortMode.TEXTURE:
            sort_key = texture.sorting_key
        elif self.__sort_mode == SpriteSortMode.FRONT_TO_BACK:
            sort_key = layer_depth
        elif self.__sort_mode == SpriteSortMode.BACK_TO_FRONT:
            sort_key = -layer_depth

        texel_width = 1.0 / texture.width
        texel_height = 1.0 / texture.height

        for i, c in enumerate(list(text)):
            c_ord = ord(c)
            source_rect = sp_sheet.frames[str(c_ord)].rect

            if c == '\r':
                continue
            if c == '\n':
                offset.x = 0
                offset.y += h
                first_char_of_line = True
                continue

            if first_char_of_line:
                offset.x = 0
                first_char_of_line = False
            else:
                offset.x += w

            item = self.__batcher.create_batch_item()

            item.texture = texture
            item.sortkey = sort_key

            self.__tex_coord_tl = glm.vec2(source_rect.left * texel_width, 1.0 - (source_rect.top * texel_height))
            self.__tex_coord_br = glm.vec2((source_rect.left + source_rect.w) * texel_width,
                                           1.0 - ((source_rect.top + source_rect.h) * texel_height))

            if self.__game.is_origin_topleft():
                self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

            if rotation == 0:
                item.set(offset.x + position.x, offset.y + position.y,
                         w, h,
                         chars_colors[i],
                         self.__tex_coord_tl, self.__tex_coord_br, layer_depth)
            else:
                item.set_extended(position.x, position.y,
                                  offset.x, offset.y,
                                  w, h,
                                  utils.sin_deg(rotation), utils.cos_deg(rotation),
                                  chars_colors[i],
                                  self.__tex_coord_tl, self.__tex_coord_br,
                                  layer_depth)

            offset.x += kerning_width

        # We need to flush if we're using Immediate sort mode.
        self.flush_if_needed()

    def draw_string_sprite_font(self, sprite_font, text, position, color):
        offset = glm.vec2(0, 0)
        first_char_of_line = True

        for c in text:
            c_ord = ord(c)

            if c == '\r':
                continue
            if c == '\n':
                offset.x = 0
                offset.y += sprite_font.line_height
                first_char_of_line = True
                continue

            current_glyph = sprite_font.glyphs[c_ord]

            if first_char_of_line:
                offset.x = max(current_glyph.xoffset, 0)
                first_char_of_line = False
            else:
                offset.x += sprite_font.spacing + current_glyph.xoffset

            texture = sprite_font.sprite_frame_list[current_glyph.page].texture
            sortkey = texture.sorting_key if self.__sort_mode == SpriteSortMode.TEXTURE else 0
            item = self.__batcher.create_batch_item()
            item.texture = texture
            item.sortkey = sortkey

            texel_width = 1.0 / texture.width
            texel_height = 1.0 / texture.height
            self.__tex_coord_tl = glm.vec2(current_glyph.x * texel_width, 1.0 - (current_glyph.y * texel_height))
            self.__tex_coord_br = glm.vec2((current_glyph.x + current_glyph.width) * texel_width,
                                           1.0 - ((current_glyph.y + current_glyph.height) * texel_height))

            if self.__game.is_origin_topleft():
                self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

            p = glm.vec2(offset)
            p.x += current_glyph.xoffset
            p.y += current_glyph.yoffset
            p += position

            item.set(p.x, p.y,
                     current_glyph.width, current_glyph.height,
                     color,
                     self.__tex_coord_tl, self.__tex_coord_br, 0)

            offset.x += current_glyph.xadvance

        # We need to flush if we're using Immediate sort mode.
        self.flush_if_needed()

    def draw_string_sprite_font_ex(self, sprite_font, text: str, position: glm.vec2, color: pg.Color,
                                   rotation: float, origin: glm.vec2, scale: glm.vec2, effects: SpriteEffects,
                                   layer_depth: float):
        flip_adjustment = glm.vec2(0)
        flipped_vert = (effects & SpriteEffects.FLIP_VERTICALLY) == SpriteEffects.FLIP_VERTICALLY
        flipped_horz = (effects & SpriteEffects.FLIP_HORIZONTALLY) == SpriteEffects.FLIP_HORIZONTALLY

        if flipped_vert or flipped_horz:
            size = sprite_font.measure_string(text)
            if flipped_horz:
                origin.x *= -1
                flip_adjustment.x = -size.x
            if flipped_vert:
                origin.y *= -1
                flip_adjustment.y = sprite_font.line_height - size.y

        transformation = glm.identity(glm.mat4)
        scale_vec = glm.vec3((-scale.x if flipped_horz else scale.x), (-scale.y if flipped_vert else scale.y), 1.0)
        scale_mat = glm.scale(transformation, scale_vec)
        trans_vec = glm.vec3(((flip_adjustment.x - origin.x) * scale_vec.x) + position.x,
                             ((flip_adjustment.y - origin.y) * scale_vec.y) + position.y,
                             0.0)
        trans_mat = glm.translate(transformation, trans_vec)
        if rotation == 0:
            transformation = trans_mat * scale_mat
        else:
            scale_rot = glm.rotate(transformation, glm.radians(rotation), glm.vec3(0, 0, 1))
            transformation = trans_mat * scale_mat * scale_rot

        offset = glm.vec2(0)
        first_char_of_line = True
        sort_key = 0.0

        for c in list(text):
            c_ord = ord(c)

            if c == '\r':
                continue
            if c == '\n':
                offset.x = 0
                offset.y += sprite_font.line_height
                first_char_of_line = True
                continue

            current_glyph = sprite_font.glyphs[c_ord]
            texture = sprite_font.sprite_frame_list[current_glyph.page].texture

            if self.__sort_mode == SpriteSortMode.TEXTURE:
                sort_key = texture.sorting_key
            elif self.__sort_mode == SpriteSortMode.FRONT_TO_BACK:
                sort_key = layer_depth
            elif self.__sort_mode == SpriteSortMode.BACK_TO_FRONT:
                sort_key = -layer_depth

            if first_char_of_line:
                offset.x = max(current_glyph.xoffset, 0)
                first_char_of_line = False
            else:
                offset.x += sprite_font.spacing + current_glyph.xoffset

            p = glm.vec2(offset)
            if flipped_horz:
                p.x += current_glyph.width
            p.x += current_glyph.xoffset

            if flipped_vert:
                p.y += current_glyph.height - sprite_font.line_height
            p.y += current_glyph.yoffset

            p = transformation * glm.vec4(p.x, p.y, 0, 1)

            item = self.__batcher.create_batch_item()
            item.texture = texture
            item.sortkey = sort_key

            texel_width = 1.0 / texture.width
            texel_height = 1.0 / texture.height
            self.__tex_coord_tl = glm.vec2(current_glyph.x * texel_width, 1.0 - (current_glyph.y * texel_height))
            self.__tex_coord_br = glm.vec2((current_glyph.x + current_glyph.width) * texel_width,
                                           1.0 - ((current_glyph.y + current_glyph.height) * texel_height))

            if self.__game.is_origin_topleft():
                self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

            if effects & SpriteEffects.FLIP_VERTICALLY:
                self.__tex_coord_tl.y, self.__tex_coord_br.y = self.__tex_coord_br.y, self.__tex_coord_tl.y

            if effects & SpriteEffects.FLIP_HORIZONTALLY:
                self.__tex_coord_tl.x, self.__tex_coord_br.x = self.__tex_coord_br.x, self.__tex_coord_tl.x

            if rotation == 0:
                item.set(p.x, p.y,
                         current_glyph.width * scale.x, current_glyph.height * scale.y,
                         color,
                         self.__tex_coord_tl, self.__tex_coord_br, layer_depth)
            else:
                item.set_extended(p.x, p.y,
                                  0, 0,
                                  current_glyph.width * scale.x, current_glyph.height * scale.y,
                                  utils.sin_deg(rotation), utils.cos_deg(rotation),
                                  color,
                                  self.__tex_coord_tl, self.__tex_coord_br, layer_depth)

            offset.x += current_glyph.xadvance

        # We need to flush if we're using Immediate sort mode.
        self.flush_if_needed()

    def dispose(self):
        self.__batcher.dispose()
