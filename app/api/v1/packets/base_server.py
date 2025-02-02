import json
from abc import abstractmethod, ABC
from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.packets.base import BasePacket


class ServerPacket(BasePacket, ABC):
    PACKET_CLASS = PacketClass.SERVER
    
    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass

    def pack(self) -> str:
        packet: Dict[str, Any] = {
            "data": self.to_json(),
            "meta": {
                "tag": self.PACKET_TAG,
                "class": self.PACKET_CLASS.value
            }
        }

        return json.dumps(packet)
