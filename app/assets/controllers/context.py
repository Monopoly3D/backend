from abc import ABC, abstractmethod
from typing import Any


class ContextController(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(
            self,
            *args,
            **kwargs
    ) -> None:
        pass

    @abstractmethod
    def get(
            self,
            *args,
            **kwargs
    ) -> Any:
        pass

    @abstractmethod
    def exists(
            self,
            *args,
            **kwargs
    ) -> bool:
        pass

    @abstractmethod
    def remove(
            self,
            *args,
            **kwargs
    ) -> None:
        pass
