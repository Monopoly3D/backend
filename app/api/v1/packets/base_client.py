from abc import abstractmethod, ABC
from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ClientPacket(BasePacket, ABC):
    PACKET_CLASS = PacketClass.CLIENT

    @classmethod
    @abstractmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        pass

    @classmethod
    def unpack(cls, packet: str) -> 'ClientPacket':
        packet: Dict[str, Any] = cls._get_validated_packet(packet)

        if packet["meta"]["tag"] != cls.PACKET_TAG or packet["meta"]["class"] != cls.PACKET_CLASS.value:
            raise InvalidPacketError("Provided packet meta is invalid")

        return cls.from_json(packet["data"])
