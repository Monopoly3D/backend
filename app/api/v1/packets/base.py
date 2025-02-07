from abc import abstractmethod, ABC
from abc import abstractmethod, ABC
from typing import Any

from app.api.v1.enums.packet_class import PacketClass


class BasePacket(ABC):
    PACKET_TAG: str
    PACKET_CLASS: PacketClass

    @abstractmethod
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        pass
