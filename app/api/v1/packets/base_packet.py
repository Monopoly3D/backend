import json
from abc import abstractmethod, ABC
from typing import Dict, Any, List, Type

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
    def unpack(cls, packet: str) -> 'BasePacket':
        try:
            packet: Dict[str, Any] = json.loads(packet)
        except ValueError:
            raise InvalidPacketError("Provided packet is not a valid JSON")

        if "data" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        invalid_packet_meta = InvalidPacketError("Provided packet meta is invalid")

        if "meta" not in packet:
            raise invalid_packet_meta

        for meta_attribute in ("tag", "class"):
            if meta_attribute not in packet["meta"]:
                raise invalid_packet_meta

        if cls == BasePacket:
            packet_tag: str = packet["meta"]["tag"]
            packet_class: Type[BasePacket] = {p.PACKET_TAG: p for p in cls.__get_packets()}[packet_tag]

            if packet_class.PACKET_CLASS != packet["meta"]["class"]:
                raise invalid_packet_meta

            return packet_class.from_json(packet["data"])
        else:
            if packet["meta"]["tag"] != cls.PACKET_TAG:
                raise invalid_packet_meta
            if packet["meta"]["class"] != cls.PACKET_CLASS.value:
                raise invalid_packet_meta

            return cls.from_json(packet["data"])

    def pack(self) -> Dict[str, Any] | str:
        packet: Dict[str, Any] = {
            "data": self.to_json(),
            "meta": {
                "tag": self.PACKET_TAG,
                "class": self.PACKET_CLASS.value
            }
        }

        return json.dumps(packet)

    @classmethod
    def __get_packets(cls) -> List[Type['BasePacket']]:
        subclasses: List[Type[BasePacket]] = cls.__subclasses__()
        overall: List[Type[BasePacket]] = []

        for subclass in subclasses:
            overall.append(subclass)
            overall.extend(subclass.__get_packets())

        return overall
