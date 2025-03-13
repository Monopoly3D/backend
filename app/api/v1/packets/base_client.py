import json
from abc import abstractmethod, ABC
from typing import Dict, Any, Type, List

from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.packets.base import BasePacket


@dataclass
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

        try:
            return cls.from_json(packet["data"])
        except KeyError or ValueError or ValidationError:
            raise InvalidPacketDataError("Provided packet data is invalid")

    @classmethod
    def withdraw_packet(
            cls,
            packet: str
    ) -> 'ClientPacket':
        try:
            packet_type: Type[ClientPacket] = ClientPacket.withdraw_packet_type(packet)
            return packet_type.unpack(packet)
        except InvalidPacketError:
            raise InvalidPacketDataError("Provided packet data is invalid")

    @classmethod
    def withdraw_packet_type(
            cls,
            packet: str
    ) -> Type['ClientPacket']:
        packet: Dict[str, Any] = cls._get_validated_packet(packet)

        packet_tag: str = packet["meta"]["tag"]
        packet_class: str = packet["meta"]["class"]

        packets: Dict[str, Type[ClientPacket]] = {
            p.PACKET_TAG: p for p in cls.__get_packets() if p.PACKET_CLASS.value == packet_class
        }

        if packet_tag not in packets:
            raise InvalidPacketError("Provided packet meta is invalid")

        return packets[packet_tag]

    @classmethod
    def _get_validated_packet(
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

        return packet

    @classmethod
    def __get_packets(cls) -> List[Type['ClientPacket']]:
        subclasses: List[Type[ClientPacket]] = cls.__subclasses__()
        overall: List[Type[ClientPacket]] = []

        for subclass in subclasses:
            overall.append(subclass)
            overall.extend(subclass.__get_packets())

        return overall
