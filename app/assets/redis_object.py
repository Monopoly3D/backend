from abc import ABC, abstractmethod
from typing import Any, Dict


class RedisObject(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, data: Dict[str, Any]) -> 'RedisObject': pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]: pass
