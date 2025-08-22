from abc import ABC, abstractmethod
from typing import Any, Dict


class GameObject(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass
