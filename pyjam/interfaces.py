from abc import ABC, abstractmethod


class IDisposable(ABC):
    @abstractmethod
    def dispose(self):
        pass


"""
class IGameComponent(ABC):
    @abstractmethod
    def initialize(self):
        pass


class IUpdatable(ABC):
    @abstractmethod
    def update(self, delta_time: float):
        pass

    @property
    @abstractmethod
    def enabled(self) -> bool:
        pass

    @property
    @abstractmethod
    def update_order(self) -> int:
        pass


class IRenderable(ABC):
    @abstractmethod
    def render(self, delta_time: float):
        pass

    @property
    @abstractmethod
    def render_order(self) -> int:
        pass

    @property
    @abstractmethod
    def visible(self) -> bool:
        pass


class GameComponent(IGameComponent, IUpdatable):
    def __init__(self, game):
        self._enabled = True
        self._update_order = 0
        self._game = game

    def initialize(self):
        pass

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def update_order(self) -> int:
        return self._update_order

    @update_order.setter
    def update_order(self, value):
        self._update_order = value

    def update(self, delta_time: float):
        pass


class RenderableComponent(GameComponent,IRenderable):
    def __init__(self, game):
        super().__init__(game)
        self._initialized = False
        self._render_order = 0
        self._visible = True

    def render(self, delta_time: float):
        pass

    @property
    def render_order(self) -> int:
        return self._render_order

    @render_order.setter
    def render_order(self, value):
        self._render_order = value

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    def initialize(self):
        self._initialized = True


class GameComponentCollection:
    def __init__(self):
        self.components = []
"""
