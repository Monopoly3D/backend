from abc import abstractmethod, ABC
from typing import Dict, Any

from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ClientPacket(BasePacket, ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        pass

    @classmethod
    def unpack(cls, packet: str) -> 'BasePacket':
        packet: Dict[str, Any] = cls.__get_validated_packet(packet)

        if packet["meta"]["tag"] != cls.PACKET_TAG or packet["meta"]["class"] != cls.PACKET_CLASS.value:
            raise InvalidPacketError("Provided packet meta is invalid")

        return cls.from_json(packet["data"])
