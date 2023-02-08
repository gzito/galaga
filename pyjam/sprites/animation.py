from pyjam.sprites.frame import SpriteFrame


class Animation2D:
    DEFAULT_ANIM_FPS = 10

    def __init__(self):
        # frames list
        self.__frames = []

        # fps
        self.__fps = self.DEFAULT_ANIM_FPS

        # frame duration in seconds
        self.__frame_duration_secs = 0.0

        # total duration of the animation in seconds
        self.__total_duration = 0.0

        # indicates if the animation keeps play looping
        self.__loop = True

        # Total number of frames the sprite managed to get from its image.
        # May be less than the number of frames in self.__frames
        self.__frames_count = 0

        # TODO
        # flip all the frames around x
        # self.__flipx = False

        # TODO
        # flip all the frames around y
        # self.__flipy = False

        # animation speed multiplier
        self.__speed = 1.0

        # flag to know if the animation has started
        self.__is_playing = False

        # current time of the animation (secs)
        self.__current_time = 0.0

        # index of animation's start frame
        self.__start_frame_idx = 0

        # index of animation's end frame
        self.__end_frame_idx = 0

        # index of the list corresponding to the displayed frame
        self.__current_frame_index = 0

    @property
    def fps(self) -> int:
        return self.__fps

    @property
    def frames_count(self) -> int:
        return self.__frames_count

    @property
    def current_frame(self) -> SpriteFrame:
        return self.__frames[self.__current_frame_index]

    def is_loop_enabled(self) -> bool:
        return self.__loop

    def is_playing(self) -> bool:
        return self.__is_playing

    def add_frame(self, frame: SpriteFrame):
        # adds a frame to the list
        self.__frames.append(frame)

    def play(self, fps: int = DEFAULT_ANIM_FPS, loop: bool = True, start_frame_idx: int = 0, end_frame_idx: int = -1):
        self.__fps = fps
        self.__loop = loop
        self.__frame_duration_secs = 1.0 / self.__fps
        self.__start_frame_idx = start_frame_idx
        if end_frame_idx == -1:
            self.__frames_count = len(self.__frames)
            self.__end_frame_idx = self.__frames_count - 1
        else:
            self.__frames_count = end_frame_idx - start_frame_idx + 1
            self.__end_frame_idx = end_frame_idx

        self.__total_duration = self.__frame_duration_secs * self.__frames_count
        self.__current_time = 0
        self.__is_playing = True

    def stop(self):
        self.__is_playing = False

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
                self.__current_frame_index = self.__start_frame_idx + \
                                             round(elapsed / self.__frame_duration_secs) % self.__frames_count
            else:
                self.__current_frame_index = -1
