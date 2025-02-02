from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.websocket.game_not_found_error import GameNotFoundError
from app.api.v1.exceptions.websocket.max_players import MaxPlayersError
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.logging import logger
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGame
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPingPacket)
async def on_client_ping(packet: ClientPingPacket) -> ServerPingPacket:
    logger.info(f"Ping: {packet.request}")

    return ServerPingPacket("Pong!")


@games_packets_router.handle(ClientPlayerJoinGame)
async def on_client_join_game(
        websocket: WebSocket,
        packet: ClientPlayerJoinGame,
        user: User,
        connections: ConnectionsController,
        games_controller: GamesController
) -> None:
    game: Game | None = await games_controller.get_game(packet.game_id, connections)

    if game is None:
        raise GameNotFoundError("Game with provided UUID was not found")

    if len(game.players) >= game.MAX_PLAYERS:
        raise MaxPlayersError("Game with provided UUID has reached maximum number of players")

    if game.has_player(user.user_id):
        raise PlayerAlreadyInGameError("Player has already joined this game")

    player = Player(
        user.user_id,
        username=user.username,
        connection=websocket
    )
    game.add_player(player)

    await game.save()

    for connection in game.get_connections():
        await connection.send_text(ServerPlayerJoinGamePacket(game.game_id, player.player_id, player.username).pack())
