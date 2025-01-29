from enum import Enum
from typing import Tuple

from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket


class PacketType(Enum):
    CLIENT_PING = ClientPingPacket
    SERVER_PING = ServerPingPacket

    @property
    def tags(self) -> Tuple[str, ...]:
        return self.__tags()

    @classmethod
    def __tags(cls) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(packet.value.PACKET_TAG for packet in cls))
