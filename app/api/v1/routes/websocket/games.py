import asyncio
from asyncio import Task
from typing import Annotated

from starlette.websockets import WebSocket

from app.api.v1.exceptions.websocket.game_not_awaiting_move import GameNotAwaitingMoveError
from app.api.v1.exceptions.websocket.max_players import TooManyPlayersError
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGamePacket
from app.api.v1.packets.client.player_move import ClientPlayerMovePacket
from app.api.v1.packets.client.player_ready import ClientPlayerReadyPacket
from app.api.v1.packets.server.game_countdown_start import ServerGameCountdownStartPacket
from app.api.v1.packets.server.game_countdown_stop import ServerGameCountdownStopPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.api.v1.routes.websocket import dependencies
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User
from app.assets.utils import get_task
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPingPacket)
async def on_ping() -> ServerPingPacket:
    return ServerPingPacket()


@games_packets_router.handle(ClientPlayerJoinGamePacket)
async def on_client_join_game(
        websocket: WebSocket,
        user: User,
        game: Annotated[Game, dependencies.get_game(is_started=False, has_player=False)]
) -> None:
    if len(game.players) >= game.max_players:
        raise TooManyPlayersError("Game with provided UUID has too many players")

    if game.has_player(user.user_id):
        raise PlayerAlreadyInGameError("You are already in game")

    player = Player(user.user_id, username=user.username)
    player.connection = websocket

    game.add_player(player)
    await game.save()
    await game.send(ServerPlayerJoinGamePacket(game.game_id, player))


@games_packets_router.handle(ClientPlayerReadyPacket)
async def on_client_ready(
        packet: ClientPlayerReadyPacket,
        player: Annotated[Player, dependencies.get_player(game_has_started=False)]
) -> None:
    player.is_ready = packet.is_ready
    game: Game = player.game

    await game.save()
    await game.send(ServerPlayerReadyPacket(game.game_id, player.player_id, packet.is_ready))

    task: Task | None = get_task(f"start:{game.game_id}")

    if game.is_ready and task is None and len(game.players) >= game.min_players:
        task = asyncio.create_task(game.delayed_start(), name=f"start:{game.game_id}")
        await game.send(ServerGameCountdownStartPacket(game.game_id))
        await task
    elif not game.is_ready and task is not None:
        await game.send(ServerGameCountdownStopPacket(game.game_id))
        task.cancel()


@games_packets_router.handle(ClientPlayerMovePacket)
async def on_client_move(
        game: Annotated[Game, dependencies.get_game()],
        player: Annotated[Player, dependencies.get_player(game_has_started=True)]
) -> None:
    if not game.awaiting_move or game.players_list[game.move].player_id != player.player_id:
        raise GameNotAwaitingMoveError("You are not allowed to move now")

    await game.move_player()
    await game.save()
