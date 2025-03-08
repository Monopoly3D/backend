from typing import Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_got_imprisoned import ServerPlayerGotImprisonedPacket
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


@dataclass
class Police(Field):
    field_type: FieldType = FieldType.POLICE

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        player.prison = 0
        player.double_amount = 0
        player.field = self.game.fields.police

        await self.game.send(
            ServerPlayerGotImprisonedPacket(self.game.game_id, player.player_id, self.game.fields.police)
        )

        await self.game.next()
