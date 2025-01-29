from enum import Enum
from typing import Tuple

from app.api.v1.enums.packet_class import PacketClass


class PacketType(Enum):
    CLIENT_PING = "ping", PacketClass.CLIENT
    SERVER_PING = "ping", PacketClass.SERVER

    def __new__(
            cls,
            packet_tag: str,
            packet_class: PacketClass
    ) -> 'PacketType':
        obj = object.__new__(cls)
        obj._value_ = (packet_tag, packet_class)

        obj.packet_tag = packet_tag
        obj.packet_class = packet_class

        return obj

    @property
    def tags(self) -> Tuple[str, ...]:
        return self.__tags()

    @classmethod
    def __tags(cls) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(packet.packet_tag for packet in cls))
