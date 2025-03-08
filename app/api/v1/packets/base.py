from abc import abstractmethod, ABC
from typing import Any, ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.enums.packet_class import PacketClass


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BasePacket(ABC):
    PACKET_TAG: ClassVar[str]
    PACKET_CLASS: ClassVar[PacketClass]

    @abstractmethod
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        pass
