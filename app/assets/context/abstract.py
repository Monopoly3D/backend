from abc import ABC, abstractmethod
from typing import Any


class AbstractContext(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def setup(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def to_json(self) -> Any:
        pass
