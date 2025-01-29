import json
from abc import abstractmethod, ABC
from typing import Dict, Any

from app.api.v1.enums.packet_type import PacketType
from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError


class BasePacket(ABC):
    packet_type: PacketType

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
            raise InvalidPacketError("Provided packet does not contain data")
        if "meta" not in packet:
            raise InvalidPacketError("Provided packet does not contain meta")

        for meta_attribute in ("id", "tag", "class"):
            if meta_attribute not in packet:
                raise InvalidPacketError("Provided packet meta is invalid")

        if packet["id"] != cls.packet_type.packet_id:
            raise InvalidPacketError("Provided packet ID is invalid")
        if packet["tag"] != cls.packet_type.packet_tag:
            raise InvalidPacketError("Provided packet tag is invalid")
        if packet["class"] != cls.packet_type.packet_class.value:
            raise InvalidPacketError("Provided packet class is invalid")

        return cls.from_json(packet["data"])

    def pack(
            self,
            *,
            to_string: bool = False
    ) -> Dict[str, Any] | str:
        packet: Dict[str, Any] = {
            "data": self.to_json(),
            "meta": {
                "id": self.packet_type.packet_id,
                "tag": self.packet_type.packet_tag,
                "class": self.packet_type.packet_class.value
            }
        }

        if to_string:
            return json.dumps(packet)

        return packet
