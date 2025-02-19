from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_got_imprisoned import ServerPlayerGotImprisonedPacket
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field
from app.assets.objects.player import Player


@dataclass
class Police(Field):
    field_type: FieldType = FieldType.POLICE

    async def on_stand(
            self,
            player: Player,
            amount: int
    ) -> None:
        player.is_imprisoned = True
        player.field = self.game.police

        await self.game.send(
            ServerPlayerGotImprisonedPacket(self.game.game_id, player.player_id, self.game.police)
        )
