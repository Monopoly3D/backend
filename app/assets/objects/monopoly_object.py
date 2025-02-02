from abc import ABC, abstractmethod
from typing import Any, Dict


class MonopolyObject(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass
