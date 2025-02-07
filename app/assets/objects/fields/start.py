from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_got_start_reward import ServerPlayerGotStartRewardPacket
from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Start(Field):
    async def on_stand(
            self,
            player: Player
    ) -> None:
        player.balance += self.game.start_reward

        await self.game.send(
            ServerPlayerGotStartRewardPacket(self.game.game_id, player.player_id, player.balance)
        )
