from functools import wraps
from typing import Callable

from exc import RateLimitExceeded
from strategies.bases import RateStratBase


def strat_set_check(fn):
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_rate_strat'):
            raise RuntimeError('rate_strat had not set')
        return await fn(self, *args, **kwargs)
    return wrapper

class RateLimiter:
    def __init__(self, strat_factory: Callable[[str], RateStratBase]):
        self._rate_strat: RateStratBase
        self.__strat_factory = strat_factory

    @property
    def rate_strat(self) -> RateStratBase:
        return self._rate_strat

    def set_strat(self, strat_type: str):
        self._rate_strat = self.__strat_factory(strat_type)

    @strat_set_check
    async def check_rate_limit(self, ip) -> bool:
        try:
            return await self._rate_strat.pass_limit(ip)
        except RateLimitExceeded:
            return False
