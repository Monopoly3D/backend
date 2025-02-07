from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.enums.imprison_cause import ImprisonCause


class ServerPlayerGotImprisonedPacket(ServerPacket):
    PACKET_TAG = "player_got_imprisoned"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            field: int,
            imprison_cause: ImprisonCause = ImprisonCause.POLICE
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.field = field
        self.imprison_cause = imprison_cause

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "field": self.field,
            "imprison_cause": self.imprison_cause.value
        }
