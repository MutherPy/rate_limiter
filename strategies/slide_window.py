from typing import Type

from exc import RateLimitExceeded
from strategies.bases import RateStratBase, ConfigBase
from dataclasses import dataclass
from os import getenv
from time import monotonic
from collections import deque

from strategies.types import StrategyType


@dataclass
class SlideWindowConfig(ConfigBase):
    window_limit: int
    window_step: int

    @classmethod
    def build(cls):
        return SlideWindowConfig(
            window_limit=int(getenv("SLIDE_WINDOW_LIMIT", 5)),
            window_step=int(getenv("SLIDE_WINDOW_STEP", 1)),
        )


class Window:
    def __init__(self, window_limit: int, window_step: int):
        self.window_limit = window_limit
        self.window_step = window_step
        self.window = deque(maxlen=window_limit)

    def check_limits(self) -> bool:
        while len(self.window) and monotonic() - self.window[0] > self.window_step:
            self.window.popleft()

        if len(self.window) < self.window_limit:
            self.window.append(monotonic())
            return True
        else:
            return False

    def __repr__(self) -> str:
        return f"SlideWindow({len(self.window)})"


class SlideWindowStrat(RateStratBase):
    __strategy_type__ = StrategyType.SlideWindow
    __config__ = SlideWindowConfig
    __default_processor__ = Window

    def __init__(self, config: SlideWindowConfig, window_class: Type[Window]):
        self.config = config
        self.window_class = window_class
        self.window_per_ip: dict[str, window_class] = {}

    async def pass_limit(self, ip) -> bool:
        if ip not in self.window_per_ip:
            self.window_per_ip[ip] = self.window_class(self.config.window_limit, self.config.window_step)
        if self.window_per_ip[ip].check_limits():
            return True
        else:
            raise RateLimitExceeded()

    @classmethod
    def build(cls, config: SlideWindowConfig, _class = Window):
        return SlideWindowStrat(config, _class)
