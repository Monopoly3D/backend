import json
from abc import abstractmethod, ABC
from typing import Dict, Any, List, Type

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError


class BasePacket(ABC):
    PACKET_TAG: str
    PACKET_CLASS: PacketClass

    PACKET_KEYS: Dict[str, Any]

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
    def unpack(cls, packet: str) -> 'BasePacket':
        packet: Dict[str, Any] = cls.__get_validated_packet(packet)

        if packet["meta"]["tag"] != cls.PACKET_TAG or packet["meta"]["class"] != cls.PACKET_CLASS.value:
            raise InvalidPacketError("Provided packet meta is invalid")

        return cls.from_json(packet["data"])

    def pack(self) -> str:
        packet: Dict[str, Any] = {
            "data": self.to_json(),
            "meta": {
                "tag": self.PACKET_TAG,
                "class": self.PACKET_CLASS.value
            }
        }

        return json.dumps(packet)

    @classmethod
    def withdraw_packet_type(
            cls,
            packet: str
    ) -> Type['BasePacket']:
        packet: Dict[str, Any] = cls.__get_validated_packet(packet)

        packet_tag: str = packet["meta"]["tag"]
        packets: Dict[str, Type[BasePacket]] = {p.PACKET_TAG: p for p in cls.__get_packets()}

        if packet_tag not in packets:
            raise InvalidPacketError("Provided packet meta is invalid")

        return packets[packet_tag]

    @classmethod
    def __get_validated_packet(
            cls,
            packet: str
    ) -> Dict[str, Any]:
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

        if not cls.__validate_keys(packet["data"], cls.PACKET_KEYS):
            raise InvalidPacketError("Provided packet data is invalid")

        return packet

    @classmethod
    def __validate_keys(
            cls,
            packet: Dict[str, Any],
            keys: Dict[str, Any] | List[str]
    ) -> bool:
        if isinstance(keys, dict):
            for key, value in keys.items():
                if key not in packet or not cls.__validate_keys(packet[key], value):
                    return False
        elif isinstance(keys, list):
            for key in keys:
                if key not in packet:
                    return False
        return True

    @classmethod
    def __get_packets(cls) -> List[Type['BasePacket']]:
        subclasses: List[Type[BasePacket]] = cls.__subclasses__()
        overall: List[Type[BasePacket]] = []

        for subclass in subclasses:
            overall.append(subclass)
            overall.extend(subclass.__get_packets())

        return overall
