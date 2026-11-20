from enum import StrEnum


class StrategyType(StrEnum):
    SlideWindow = "SlideWindow"
    TokenBucket = "TokenBucket"
