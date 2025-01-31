from abc import ABC, abstractmethod
from typing import Any, Dict


class MonopolyObject(ABC):
    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass
