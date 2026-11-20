from rate_limiter.strategies.bases import RateStratBase


class ImMemoryStrat(RateStratBase):
    __strategy_type__ = "memory"

    async def pass_limit(self, ip) -> bool:
        ...

    @classmethod
    def build(cls, config):
        ...