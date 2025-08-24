from typing import Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.game_ask_player_on_casino import ServerGameAskPlayerOnCasinoPacket
from app.assets.enums.field_type import FieldType
from app.assets.objects.actions.casino import CasinoAction
from app.assets.objects.fields.abstract import AbstractField


@dataclass
class Casino(AbstractField):
    FIELD_TYPE = FieldType.CASINO

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        self.game.action = CasinoAction()

        await self.game.send(
            ServerGameAskPlayerOnCasinoPacket(
                player.player_id
            )
        )
