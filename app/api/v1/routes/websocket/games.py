from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.logging import logger
from app.api.v1.packets.client.join_game import ClientJoinGamePacket
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPingPacket)
async def on_client_ping(packet: ClientPingPacket) -> ServerPingPacket:
    logger.info(f"Received message: {packet.request}")

    return ServerPingPacket("Message received!")


@games_packets_router.handle(ClientJoinGamePacket)
async def on_client_join_game(
        websocket: WebSocket,
        packet: ClientJoinGamePacket,
        user: User,
        connections: ConnectionsController,
        games_controller: GamesController
) -> ServerPingPacket:
    game: Game | None = await games_controller.get_game(packet.game_id, connections)

    if game.has_player(user.user_id):
        raise PlayerAlreadyInGameError("Game with provided UUID already has this player")

    game.add_player(
        Player(
            user.user_id,
            username=user.username,
            connection=websocket
        )
    )

    await game.save()
    return ServerPingPacket("join")
