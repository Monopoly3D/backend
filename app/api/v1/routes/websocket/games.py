from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.websocket.game_not_found import GameNotFoundError
from app.api.v1.exceptions.websocket.max_players import MaxPlayersError
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.exceptions.websocket.player_not_found import PlayerNotFoundError
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGamePacket
from app.api.v1.packets.client.player_ready import ClientPlayerReadyPacket
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPlayerJoinGamePacket)
async def on_client_join_game(
        websocket: WebSocket,
        packet: ClientPlayerJoinGamePacket,
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

    await game.send(ServerPlayerJoinGamePacket(game.game_id, player))


@games_packets_router.handle(ClientPlayerReadyPacket)
async def on_client_ready(
        packet: ClientPlayerReadyPacket,
        user: User,
        connections: ConnectionsController,
        games_controller: GamesController
) -> None:
    game: Game | None = await games_controller.get_game(packet.game_id, connections)

    if game is None:
        raise GameNotFoundError("Game with provided UUID was not found")

    player: Player | None = game.get_player(user.user_id)

    if player is None:
        raise PlayerNotFoundError("Player with provided UUID was not found")

    player.is_ready = packet.is_ready
    await game.save()

    await game.send(ServerPlayerReadyPacket(game.game_id, player.player_id, packet.is_ready))
