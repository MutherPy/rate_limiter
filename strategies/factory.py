from typing import Any

from strategies.bases import RateStratBase
from strategies.registry import StrategyRegistry, StrategyConfigRegistry


def strat_factory(strat_type: str) -> RateStratBase:
    strat: tuple[RateStratBase, Any] | None
    if (strat := StrategyRegistry.get(strat_type)) is not None:
        config = StrategyConfigRegistry.get(strat_type)
        return strat[0].build(config=config.build(), _class=strat[1])
    else:
        raise ValueError(f"Unknown strategy type: {strat_type}")
