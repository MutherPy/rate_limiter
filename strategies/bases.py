from abc import ABCMeta, ABC, abstractmethod
from typing import Self, TypeVar, Any

from strategies.registry import StrategyRegistry, StrategyConfigRegistry
from strategies.types import StrategyType


class ConfigBase(ABC):
    @classmethod
    @abstractmethod
    def build(cls) -> 'Self':
        pass

StratConfig = TypeVar('StratConfig', bound=ConfigBase)


class StratRegistrationMeta(ABCMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if "__strategy_type__" in attrs:
            print(attrs["__strategy_type__"], cls, __file__)
            if StrategyRegistry.get(attrs["__strategy_type__"]) is None:
                StrategyRegistry[attrs["__strategy_type__"]] = (cls, attrs["__default_processor__"])
                StrategyConfigRegistry[attrs["__strategy_type__"]] = attrs["__config__"]
            else:
                raise RuntimeError('Duplicate start name')

class RateStratBase(ABC, metaclass=StratRegistrationMeta):
    __strategy_type__: StrategyType
    __config__: StratConfig
    __default_processor__: Any

    def __str__(self) -> str:
        return f'Type -> {self.__strategy_type__}, Config -> {self.__config__}'

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    async def pass_limit(self, ip) -> bool:
        pass

    @classmethod
    @abstractmethod
    def build(cls, config: StratConfig, _class: Any) -> 'Self':
        pass
