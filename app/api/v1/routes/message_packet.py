import json
from typing import Dict, Any, Self


class MessagePacket:
    id = 1
    name = "message"

    def __init__(
            self,
            message: str
    ) -> None:
        self.message: str = message

    def pack(
            self,
            *,
            to_string: bool = False
    ) -> Dict[str, Any] | str:
        packet: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "message": self.message
        }

        if to_string:
            return json.dumps(packet)

        return packet

    @classmethod
    def unpack(
            cls,
            packet: Dict[str, Any] | str,
            *,
            from_string: bool = False
    ) -> Self:
        if from_string:
            packet = json.loads(packet)

        if packet.get("id") != cls.id:
            raise ValueError("MessagePacket ID mismatch")

        return cls(packet.get("message"))
