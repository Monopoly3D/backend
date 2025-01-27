from arq import ArqRedis

from app.api.v1.controllers.games import GamesController


async def update_recruitments(ctx: ArqRedis):
    games: GamesController = GamesController(ctx["redis"])

    await games.update_recruitments()
