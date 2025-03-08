from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.enums.imprison_cause import ImprisonCause


@dataclass
class ServerPlayerGotImprisonedPacket(ServerPacket):
    PACKET_TAG = "player_got_imprisoned"

    game_id: UUID
    player_id: UUID
    field: int
    imprison_cause: ImprisonCause = ImprisonCause.POLICE

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "field": self.field,
            "imprison_cause": self.imprison_cause.value
        }
