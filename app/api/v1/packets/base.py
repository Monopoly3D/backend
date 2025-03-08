from abc import ABC
from typing import ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.enums.packet_class import PacketClass


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BasePacket(ABC):
    PACKET_TAG: ClassVar[str]
    PACKET_CLASS: ClassVar[PacketClass]
