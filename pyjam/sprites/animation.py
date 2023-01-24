from pyjam.sprites.frame import SpriteFrame

DEFAULT_ANIM_FPS = 10


class Animation2D:
    def __init__(self, fps=DEFAULT_ANIM_FPS, loop: bool = True):
        # frames list
        self.__frames = []

        # fps
        self.__fps = fps

        # frame duration
        self.__frame_duration_secs = 1.0 / self.__fps

        # total duration of the animation in seconds
        self.__total_duration = self.__frame_duration_secs * len(self.__frames)

        # indicates if the animation keeps play looping
        self.__loop = loop

        """
        TODO
        # flip all the frames around x
        self.__flipx = False

        # flip all the frames around y
        self.__flipy = False
        """

        # animation speed multiplier
        self.__speed = 1.0

        # flag to know if the animation has started
        self.__is_playing = False

        # current time of the animation (secs)
        self.__current_time = 0.0

        # index of the list corresponding to the displayed frame
        self.__current_frame_index = 0

    @property
    def fps(self):
        return self.__fps

    @fps.setter
    def fps(self, value):
        self.__fps = value
        self.__frame_duration_secs = 1.0 / value
        self.__total_duration = self.__frame_duration_secs * len(self.__frames)

    def is_loop_enabled(self):
        return self.__loop

    def enable_loop(self, bflag):
        self.__loop = bflag

    def add_frame(self, frame: SpriteFrame):
        # adds a frame to the list
        self.__frames.append(frame)
        self.__total_duration = self.__frame_duration_secs * len(self.__frames)

    def get_current_frame(self) -> SpriteFrame:
        return self.__frames[self.__current_frame_index]

    def play(self, restart: bool = True):
        if restart:
            self.__current_time = 0
        self.__is_playing = True

    def restart(self):
        self.play(True)

    def stop(self):
        self.__is_playing = False

    def is_playing(self):
        return self.__is_playing

    # delta time is in msecs
    def update(self, delta_time: float):
        if self.__is_playing:
            # calculate the time
            self.__current_time += delta_time * self.__speed
            elapsed = self.__current_time

            # handles the end of animation and the loop flag
            if elapsed >= self.__total_duration:
                if self.__loop:
                    elapsed = elapsed % self.__total_duration
                else:
                    self.stop()

            # calculates the current frame based on time
            if self.__is_playing:
                self.__current_frame_index = round(elapsed / self.__frame_duration_secs) % len(self.__frames)
            else:
                self.__current_frame_index = -1
