from enum import Enum
from typing import Tuple

from app.api.v1.enums.packet_class import PacketClass


class PacketType(Enum):
    CREATE_GAME_PACKET = 1, "create_game", PacketClass.CLIENT

    def __new__(
            cls,
            packet_id: int,
            packet_tag: str,
            packet_class: PacketClass
    ) -> 'PacketType':
        obj = object.__new__(cls)
        obj._value_ = {
            "id": packet_id,
            "tag": packet_tag,
            "class": packet_class
        }

        obj.packet_id = packet_id
        obj.packet_tag = packet_tag
        obj.packet_class = packet_class

        return obj

    @property
    def ids(self) -> Tuple[int, ...]:
        return self.__ids()

    @classmethod
    def __ids(cls) -> Tuple[int, ...]:
        return tuple(packet.packet_id for packet in cls)

    @property
    def tags(self) -> Tuple[str, ...]:
        return self.__tags()

    @classmethod
    def __tags(cls) -> Tuple[str, ...]:
        return tuple(packet.packet_tag for packet in cls)

    @property
    def classes(self) -> Tuple[PacketClass, ...]:
        return self.__classes()

    @classmethod
    def __classes(cls) -> Tuple[PacketClass, ...]:
        return tuple(packet.packet_class for packet in cls)
