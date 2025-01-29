import json
from abc import abstractmethod, ABC
from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError


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

    @classmethod
    @abstractmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass

    @classmethod
    def unpack(
            cls,
            packet: Dict[str, Any] | str
    ) -> 'BasePacket':
        if isinstance(packet, str):
            try:
                packet: Dict[str, Any] = json.loads(packet)
            except ValueError:
                raise InvalidPacketError("Provided packet is not a valid JSON")

        if "data" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")
        if "meta" not in packet:
            raise InvalidPacketError("Provided packet meta is invalid")

        for meta_attribute in ("tag", "class"):
            if meta_attribute not in packet["meta"]:
                raise InvalidPacketError("Provided packet meta is invalid")

        if packet["meta"]["tag"] != cls.PACKET_TAG:
            raise InvalidPacketError("Provided packet meta is invalid")
        if packet["meta"]["class"] != cls.PACKET_CLASS.value:
            raise InvalidPacketError("Provided packet meta is invalid")

        return cls.from_json(packet["data"])

    def pack(
            self,
            *,
            to_string: bool = False
    ) -> Dict[str, Any] | str:
        packet: Dict[str, Any] = {
            "data": self.to_json(),
            "meta": {
                "tag": self.PACKET_TAG,
                "class": self.PACKET_CLASS.value
            }
        }

        if to_string:
            return json.dumps(packet)

        return packet
