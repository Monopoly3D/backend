from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_got_imprisoned import ServerPlayerGotImprisonedPacket
from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Police(Field):
    async def on_stand(
            self,
            player: Player
    ) -> None:
        player.is_imprisoned = True
        player.field = self.game.police

        await self.game.send(
            ServerPlayerGotImprisonedPacket(self.game.game_id, player.player_id, self.game.police)
        )
