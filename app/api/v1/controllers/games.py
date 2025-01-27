from typing import Dict, Any
from uuid import UUID, uuid4

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.already_exists_error import AlreadyExistsError
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.game import Game


class GamesController(RedisController):
    async def create(
            self,
            uuid: UUID | str | None = None
    ) -> Game:
        if uuid is None:
            uuid = uuid4()
        else:
            if await self._exists(f"games:{uuid}"):
                raise AlreadyExistsError(f"Game with specified UUID already exists")

        game: Game = Game(uuid=uuid)
        await self._create(f"games:{game.uuid}", game.to_json())

        recruitments: Dict[str, Any] = await self._get("recruitments")

        if recruitments is None:
            recruitments = {}
        if "amount" not in recruitments:
            recruitments["amount"] = 0
        if "games" not in recruitments:
            recruitments["games"] = {}

        recruitments["games"].update({str(uuid): game.to_recruitment()})
        recruitments["amount"] = len(recruitments["games"])

        await self._create("recruitments", recruitments)

        return game

    async def get(
            self,
            uuid: UUID | str
    ) -> Game | None:
        game: Dict[str, Any] | None = await self._get(f"games:{uuid}")

        if game is None:
            raise NotFoundError(f"Game with specified UUID was not found")

        return Game.from_json(game)

    async def remove(
            self,
            uuid: UUID | str
    ) -> None:
        if not await self._exists(f"games:{uuid}"):
            raise NotFoundError(f"Game with specified UUID was not found")

        await self._remove(f"games:{uuid}")

        recruitments: Dict[str, Any] = await self._get("recruitments")

        if recruitments is None:
            recruitments = {}
        if "amount" not in recruitments:
            recruitments["amount"] = 0
        if "games" not in recruitments:
            recruitments["games"] = {}

        recruitments["games"].pop(str(uuid))
        recruitments["amount"] = len(recruitments["games"])

        await self._create("recruitments", recruitments)
