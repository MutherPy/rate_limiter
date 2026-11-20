from typing import Type

from exc import RateLimitExceeded
from strategies.bases import RateStratBase, ConfigBase
from time import monotonic
from dataclasses import dataclass
from os import getenv

from strategies.types import StrategyType


@dataclass
class BucketConfig(ConfigBase):
    size: int
    refill_per_token: float

    @classmethod
    def build(cls):
        return cls(
            size=int(getenv("BUCKET_SIZE", 10)),
            refill_per_token=float(getenv("BUCKET_REFILL_PER_TOKEN", 1.0)),
        )


class Bucket:
    def __init__(self, size: int, refill_time_per_token: float):
        self.refill_time_per_token = refill_time_per_token
        self.size = float(size)
        self.bucket = self.size
        self.last_get = 0.0

    def get_token(self) -> bool:
        now = monotonic()
        n_t = (now - self.last_get) / self.refill_time_per_token
        self.bucket = min(self.size, self.bucket + n_t)
        if self.bucket >= 1.0:
            self.bucket -= 1.0
            self.last_get = now
            return True
        else:
            return False


class BucketStrat(RateStratBase):
    __strategy_type__ = StrategyType.TokenBucket
    __config__ = BucketConfig
    __default_processor__ = Bucket

    def __init__(self, config: BucketConfig, bucket_class: Type[Bucket]):
        self.config = config
        self.bucket_per_ip: dict[str, bucket_class] = {}
        self.bucket_class = bucket_class

    async def pass_limit(self, ip) -> bool:
        if ip not in self.bucket_per_ip:
            self.bucket_per_ip[ip] = self.bucket_class(self.config.size, self.config.refill_per_token)
        if self.bucket_per_ip[ip].get_token():
            return True
        else:
            raise RateLimitExceeded()

    @classmethod
    def build(cls, config: BucketConfig, _class):
        return cls(config, _class)
