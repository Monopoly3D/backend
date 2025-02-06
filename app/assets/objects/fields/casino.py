from pydantic.dataclasses import dataclass

from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Casino(Field):
    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
