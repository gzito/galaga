import copy
import random

import glm
import pygame as pg
import moderngl as mgl

from pyjam.services.shader import ShaderService
from pyjam.services.asset import AssetService
from pyjam.services.texture import TextureService
from pyjam.services.vao import VaoService
from pyjam.services.vbo import VboService
from pyjam.sprites.batch import SpriteBatch, SpriteSortMode
from pyjam.camera import Camera
from pyjam.constants import *


class Game:
    # static access
    instance = None

    def __init__(self):
        self.services = {}

        self.__sfx = {}
        self.__audio_disabled = False

        self.__sprites = []

        self.__texts = []

        self.__bg_color = pg.Color('black')

        self.__state = None
        self.__new_state = None

        self.__clock = pg.time.Clock()
        self.__framerate: int = 0

        # elapsed secs since last frame
        self.__delta_time = 0.0

        # opengl context
        self.__ctx = None

        # this is the orginal game's resolution
        self.__virtual_display_resolution = []
        self.__virtual_display_aspect = 1.0

        # this is the actual window (or, in fullscreen, the actual screen) resolution
        self.__display_resolution = []
        self.__display_aspect = 1.0
        self.__fullscreen = False
        self.__scale_matrix = None

        self.__sp_batch = None
        self.__sp_batch_sort_mode = SpriteSortMode.BACK_TO_FRONT

        self.__camera = None

        self.__origin_at_top_left = True

        self.__assets_root = "./media"

        self.__signal_quit = False
        self.__key_state_this_frame = None
        self.__key_state_prev_frame = None
        self.__mouse_buttons_this_frame = None
        self.__mouse_buttons_prev_frame = None

        Game.instance = self

    def add_sfx(self, key, sfx):
        self.__sfx[key] = sfx

    def __get_sfx(self, key):
        return self.__sfx[key]

    def sfx_delete(self, key):
        self.__sfx.pop(key)

    def sfx_play(self, key, loops=0, maxtime=0, fade_ms=0):
        """
        begin sound playback
        The loops argument controls how many times the sample will be repeated after being played the first time.
        The default value (zero) means the Sound is not repeated, and so is only played once.
        If loops is set to -1 the Sound will loop indefinitely
        The maxtime argument can be used to stop playback after a given number of milliseconds.
        The fade_ms argument will make the sound start playing at 0 volume and fade up to full volume over the time given.
        """
        if not self.__audio_disabled:
            self.__get_sfx(key).play(loops, maxtime, fade_ms)

    def sfx_stop(self, key):
        """
        stop sound playback
        """
        if not self.__audio_disabled:
            self.__get_sfx(key).stop()

    def sfx_get_num_channels(self, key) -> int:
        """
        count how many times this sound fx is playing
        Return the number of active channels this sound is playing on
        """
        return self.__get_sfx(key).get_num_channels()

    @property
    def sprites(self):
        return self.__sprites

    @property
    def texts(self):
        return self.__texts

    @property
    def time_ms(self) -> int:
        """
        Returns the total elapsed time in milliseconds since the start of application
        """

        return pg.time.get_ticks()

    @property
    def time(self) -> float:
        """
        Returns the total elapsed time in seconds since the start of application
        """

        return self.time_ms / 1000.0

    @property
    def delta_time(self) -> float:
        """
        Returns the elapsed time in seconds from the last frame to the current one
        """
        return self.__delta_time

    @property
    def clock(self) -> pg.time.Clock:
        return self.__clock

    @property
    def ctx(self):
        return self.__ctx

    @property
    def state(self):
        return self.__state

    # path of assets folder relative to py main
    def set_assets_root(self, assets_root):
        self.__assets_root = assets_root

    def get_assets_root(self):
        return self.__assets_root

    def get_sprite_batch_sort_mode(self):
        return self.__sp_batch_sort_mode

    def set_sprite_batch_sort_mode(self, sort_mode):
        self.__sp_batch_sort_mode = sort_mode

    def get_sprite_batch(self):
        return self.__sp_batch

    @property
    def camera(self):
        return self.__camera

    def is_origin_topleft(self):
        return self.__origin_at_top_left

    def get_virtual_matrix(self):
        return self.__scale_matrix

    def set_framerate(self, framerate: int):
        self.__framerate = framerate

    def get_virtual_display_width(self) -> int:
        return self.__virtual_display_resolution[0]

    def get_virtual_display_height(self) -> int:
        return self.__virtual_display_resolution[1]

    def set_virtual_display_resolution(self, width: int, height: int):
        if width < 1:
            width = 1
        if height < 1:
            height = 1

        self.__virtual_display_resolution = [width, height]
        self.__virtual_display_aspect = width / height

    @property
    def virtual_display_aspect(self):
        return self.__virtual_display_aspect

    def get_display_width(self) -> int:
        return self.__display_resolution[0]

    def get_display_height(self) -> int:
        return self.__display_resolution[1]

    def is_fullscreen(self) -> bool:
        return self.__fullscreen

    @property
    def display_aspect(self):
        return self.__display_aspect

    def get_viewport_x_offset(self):
        return self.__ctx.viewport[0]

    def get_viewport_y_offset(self):
        return self.__ctx.viewport[1]

    def get_viewport_width(self):
        return self.__ctx.viewport[2]

    def get_viewport_height(self):
        return self.__ctx.viewport[3]

    def set_display_resolution(self, width: int, height: int, flags: int = 0, depth: int = 0, display: int = 0,
                               vsync: int = 0):
        if width < 1:
            width = 1
        if height < 1:
            height = 1

        pg.display.set_mode((width, height), flags, depth, display, vsync)

        self.__fullscreen = flags & pg.FULLSCREEN != 0
        self.__display_resolution = [width, height]
        self.__display_aspect = width / height

    def set_bg_color(self, color: pg.Color):
        self.__bg_color = color

    def clear_background(self):
        # clear framebuffer with black, i.e. draw letterbox/pillabox
        self.ctx.clear()

        # clear viewport
        self.__ctx.clear(red=self.__bg_color.r / 255, green=self.__bg_color.g / 255, blue=self.__bg_color.b / 255,
                         alpha=self.__bg_color.a / 255, depth=1.0, viewport=self.ctx.viewport)

    def signal_quit(self):
        self.__signal_quit = True

    # overridable
    def initialize(self):
        pass

    # must override
    def setup_display(self):
        pass

    # overridable
    def cleanup(self):
        pass

    def print_info(self):
        print(f'PyJam version 0.1')
        print(f'ModernGL version 5.7.4')
        print(f'OpenGL version {self.__ctx.info["GL_VERSION"]}')
        print(f'{self.__ctx.info["GL_RENDERER"]}')
        print(f'Virtual resolution: {self.get_virtual_display_width()} x {self.get_virtual_display_height()}')
        print(f'Actual resolution : {self.get_display_width()} x {self.get_display_height()}')
        print(f'Desired framerate : {self.__framerate} FPS')

    def setup(self):
        random.seed()

        pg.init()
        pg.font.init()
        pg.mixer.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        # virtual call
        self.setup_display()

        # -------------------------------------------------------------------------------
        #
        # About OpenGL coordinate system
        #
        # The default coordinate system in OpenGL is right-handed:
        # the positive x and y axes point right and up respectively,
        # and the negative z axis points forward (i.e. inside the screen).
        #
        #                   Y+
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |----------------------> X+
        #                  /
        #                 /
        #                /
        #               /
        #              /
        #             Z+
        #
        # Positive rotation is "counter-clockwise" about the axis of rotation.
        #
        # -------------------------------------------------------------------------------
        #
        # About 2d engine coordinate system
        #
        #                   -----------------------> X+
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                   |
        #                  +Y
        #
        # The positive x and y axes point right and down respectively
        # and the negative z axis points forward (i.e. inside the screen).
        #
        # Positive rotation around the z axis is "clockwise".
        #
        # -------------------------------------------------------------------------------

        # detect and use existing opengl context
        self.__ctx = mgl.create_context()

        self.setup_viewport()

        self.print_info()

        self.__ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        if self.is_origin_topleft():
            self.__ctx.front_face = 'ccw'
        else:
            self.__ctx.front_face = 'cw'
        self.__ctx.cull_face = 'back'

        self.create_services()

        # virtual call
        self.initialize()

        self.__sp_batch = SpriteBatch(self)

        scale_x = self.get_display_width() / self.get_virtual_display_width()
        scale_y = self.get_display_height() / self.get_virtual_display_height()
        self.__scale_matrix = glm.scale(glm.identity(glm.mat4), glm.vec3(scale_x, scale_y, 1.0))

        # setup camera
        eye = glm.vec3(0, 0, 4)
        self.__camera = Camera(self, eye)

        if self.__origin_at_top_left:
            left = 0
            right = self.get_display_width()
            bottom = self.get_display_height()
            top = 0
        else:
            left = -self.get_display_width() / 2
            right = self.get_display_width() / 2
            top = self.get_display_height() / 2
            bottom = -self.get_display_height() / 2

        self.__camera.set_orthographic_projection(left=left,
                                                  right=right,
                                                  bottom=bottom,
                                                  top=top,
                                                  znear=0.1,
                                                  zfar=100.0)

        self.__key_state_this_frame = copy.copy(pg.key.get_pressed())

    def setup_viewport(self):
        # print(f'display_width, display_height: {self.get_display_width()}, {self.get_display_height()}' )

        # Letterbox
        width = self.get_display_width()
        height = int(width / self.virtual_display_aspect + 0.5)

        # print(f'width, height: {width}, {height}')

        if height > self.get_display_height():
            # Pillarbox
            height = self.get_display_height()
            width = int(height * self.virtual_display_aspect + 0.5)

        vp_x = int((self.get_display_width() / 2) - (width / 2))
        vp_y = int((self.get_display_height() / 2) - (height / 2))

        # since OpenGL considers (0,0) the lower left corner of the screen
        self.ctx.viewport = (vp_x, self.get_display_height() - (vp_y + height), width, height)

    def shutdown(self):
        self.cleanup()

        self.destroy_services()

        pg.mixer.quit()
        pg.font.quit()
        pg.quit()

    def __read_input(self):
        self.__key_state_prev_frame = copy.copy(self.__key_state_this_frame)
        self.__key_state_this_frame = pg.key.get_pressed()
        self.__mouse_buttons_prev_frame = copy.copy(self.__mouse_buttons_this_frame)
        self.__mouse_buttons_this_frame = pg.mouse.get_pressed(5)

    def __state_update(self):
        if self.__state is not None:
            self.__state.handle_input()
            self.__state.update()

    def __state_late_update(self):
        if self.__state is not None:
            self.__state.late_update()

    def update(self):
        # update sprites
        for s in self.__sprites:
            s.update(self.delta_time)

    def change_state(self, new_state):
        if isinstance(new_state, type(self.__state)):
            return
        self.__new_state = new_state

    def render_state(self):
        self.__state.render()

    def render(self):
        self.__sp_batch.begin(sort_mode=self.__sp_batch_sort_mode, transform_matrix=self.get_virtual_matrix())

        for s in self.__sprites:
            if s.visible:
                s.render(self.__sp_batch)

        # draw texts
        for t in self.__texts:
            if t.visible:
                t.render(self.__sp_batch)

        self.__sp_batch.end()

    def key_up(self, key_int):
        return not self.__key_state_this_frame[key_int]

    def key_down(self, key_int):
        return self.__key_state_this_frame[key_int]

    def key_pressed(self, key_int):
        return self.__key_state_this_frame[key_int] and not self.__key_state_prev_frame[key_int]

    def mouse_button_up(self, button_num):
        return not self.__mouse_buttons_this_frame[button_num]

    def mouse_button_down(self, button_num):
        return self.__mouse_buttons_this_frame[button_num]

    def mouse_button_pressed(self, button_num):
        return self.__mouse_buttons_this_frame[button_num] and not self.__mouse_buttons_prev_frame[button_num]

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.signal_quit()
            if event.type == pg.WINDOWRESIZED:
                self.__display_resolution = [event.x, event.y]
                self.__display_aspect = float(event.x / event.y)
                self.setup_viewport()

    # ===================================================================================================
    #
    # main loop
    #
    # ===================================================================================================
    def run(self):
        self.setup()

        while not self.__signal_quit:
            self.clear_background()

            # check if state is changed since last frame
            if self.__new_state is not None:
                self.__state = self.__new_state
                self.__new_state = None
                self.__state.enter()

            self.__read_input()

            self.__camera.update()

            self.__state_update()

            self.update()

            self.__state_late_update()

            if self.__state is not None:
                self.render_state()

            self.render()

            # check if state is changed since last frame
            if self.__new_state is not None:
                self.__state.exit()

            pg.display.flip()

            # pause if necessary to achieve "FPS" frames per second
            self.__delta_time = self.clock.tick(self.__framerate) / 1000.0

            self.process_events()

        self.shutdown()

    def create_services(self):
        self.services[ASSET_SERVICE] = AssetService()
        self.services[TEXTURE_SERVICE] = TextureService(self)
        self.services[SHADER_SERVICE] = ShaderService(self)
        self.services[VBO_SERVICE] = VboService(self)
        self.services[VAO_SERVICE] = VaoService(self)

    def destroy_services(self):
        for service in self.services.values():
            service.dispose()

    def world_to_screen(self, v: glm.vec3) -> glm.vec3:
        world_mat = self.get_virtual_matrix()
        view_mat = self.camera.get_view_matrix()
        proj_mat = self.camera.get_projection_matrix()
        # parenthesis are not necessary but explanatory
        s = proj_mat * (view_mat * (world_mat * glm.vec4(v, 1)))

        vp = self.__ctx.viewport
        vp_x = vp[0]
        vp_y = vp[1]
        vp_w = vp[2]
        vp_h = vp[3]

        s[0] = (((s[0] / s[3]) + 1.0) / 2) * vp_w + vp_x
        s[1] = (((s[1] / s[3]) + 1.0) / 2) * vp_h + vp_y
        s[2] = s[2] / s[3]
        return glm.vec3(s)

    def screen_to_world(self, x: int, y: int) -> glm.vec3:
        world_mat = self.get_virtual_matrix()
        view_mat = self.camera.get_view_matrix()
        proj_mat = self.camera.get_projection_matrix()

        vp = self.__ctx.viewport
        vp_x = vp[0]
        vp_y = vp[1]
        vp_w = vp[2]
        vp_h = vp[3]
        win_z = 0.0

        """
        mat_proj = world_mat * view_mat * proj_mat
        mat_inverse = glm.inverse(mat_proj)

        inp = glm.vec3()
        inp.x = (((x-vp_x)/float(vp_w)) * 2.0) - 1.0
        inp.y = -((((y-vp_y)/float(vp_h)) * 2.0) - 1.0)
        inp.z = 2.0 * win_z - 1.0

        pos = mat_inverse * inp
        a = inp.x * mat_inverse[0, 3] + inp.y * mat_inverse[1, 3] + inp.z * mat_inverse[2, 3] + mat_inverse[3, 3]
        pos.x /= a
        pos.y /= a
        pos.z /= a
        """

        if self.is_origin_topleft():
            y = vp_h - y
        pos = glm.unProjectNO(glm.vec3(x, y, win_z), world_mat * view_mat, proj_mat, glm.vec4(vp_x, vp_y, vp_w, vp_h))
        return pos


class GameState:
    def __init__(self, game):
        self.game = game

    def handle_input(self):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass

    def late_update(self):
        pass

    def render(self):
        pass


def pc2v(coord: glm.vec2) -> glm.vec2:
    """ Converts (x,y) from percentage system to the virtual system """

    return glm.vec2(Game.instance.get_virtual_display_width() * coord.x / 100,
                    Game.instance.get_virtual_display_height() * coord.y / 100)


def pcx2vx(px: float) -> float:
    """ Converts x from percentage system to the virtual system """

    return Game.instance.get_virtual_display_width() * px / 100.0


def pcy2vy(py: float) -> float:
    """ Converts y from percentage system to the virtual system """

    return Game.instance.get_virtual_display_height() * py / 100.0


def v2pc(coord: glm.vec2) -> glm.vec2:
    """ Converts (x,y) from virtual system to the percentage system """

    return glm.vec2(coord.x / Game.instance.get_virtual_display_width() * 100.0,
                    coord.y / Game.instance.get_virtual_display_height() * 100.0)


def vx2pcx(x):
    return x / Game.instance.get_virtual_display_width() * 100.0


def vy2pcy(y):
    return y / Game.instance.get_virtual_display_height() * 100.0
