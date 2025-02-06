import asyncio
from asyncio import Task
from typing import Annotated

from starlette.websockets import WebSocket

from app.api.v1.exceptions.websocket.game_already_started import GameAlreadyStartedError
from app.api.v1.exceptions.websocket.game_not_awaiting_move import GameNotAwaitingMoveError
from app.api.v1.exceptions.websocket.game_not_started import GameNotStartedError
from app.api.v1.exceptions.websocket.max_players import TooManyPlayersError
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.exceptions.websocket.player_not_found import PlayerNotFoundError
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGamePacket
from app.api.v1.packets.client.player_move import ClientPlayerMovePacket
from app.api.v1.packets.client.player_ready import ClientPlayerReadyPacket
from app.api.v1.packets.server.game_countdown_start import ServerGameCountdownStartPacket
from app.api.v1.packets.server.game_countdown_stop import ServerGameCountdownStopPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.api.v1.routes.websocket.dependencies import WebsocketDependencies
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
        game: Annotated[Game, WebsocketDependencies.get_game]
) -> None:
    if game.is_started:
        raise GameAlreadyStartedError("Game with provided UUID has already started")

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
        user: User,
        game: Annotated[Game, WebsocketDependencies.get_game]
) -> None:
    if game.is_started:
        raise GameAlreadyStartedError("Game with provided UUID has already started")

    player: Player | None = game.get_player(user.user_id)
    if player is None:
        raise PlayerNotFoundError("You are not in game")

    player.is_ready = packet.is_ready
    await game.save()
    await game.send(ServerPlayerReadyPacket(game.game_id, player.player_id, packet.is_ready))

    task: Task | None = get_task(f"start:{game.game_id}")

    if game.is_ready and len(game.players) >= game.min_players and task is None:
        task = asyncio.create_task(game.delayed_start(), name=f"start:{game.game_id}")
        await game.send(ServerGameCountdownStartPacket(game.game_id))
        await task

    elif not game.is_ready and task is not None:
        await game.send(ServerGameCountdownStopPacket(game.game_id))
        task.cancel()


@games_packets_router.handle(ClientPlayerMovePacket)
async def on_client_move(
        user: User,
        game: Annotated[Game, WebsocketDependencies.get_game]
) -> None:
    if not game.is_started:
        raise GameNotStartedError("Game with provided UUID has not been started")

    player: Player | None = game.get_player(user.user_id)
    if player is None:
        raise PlayerNotFoundError("You are not in game")

    if not game.awaiting_move or game.players_list[game.move].player_id != player.player_id:
        raise GameNotAwaitingMoveError("You are not allowed to move now")

    await game.move_player()
    await game.save()
