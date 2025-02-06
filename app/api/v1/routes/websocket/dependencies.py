from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.websocket.game_not_found import GameNotFoundError
from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.packets.base_client import ClientPacket
from app.assets.objects.game import Game
from app.assets.objects.user import User


class WebsocketDependencies:
    @staticmethod
    async def get_game(
            packet: ClientPacket,
            connections: ConnectionsController,
            games_controller: GamesController,
            user: User
    ) -> Game:
        if not hasattr(packet, "game_id"):
            raise InvalidPacketDataError("Provided packet data is invalid")

        print(getattr(packet, "game_id"))

        game: Game | None = await games_controller.get_game(getattr(packet, "game_id"), connections)

        if game is None or user.user_id not in game.players:
            raise GameNotFoundError("Game with provided UUID was not found")

        return game
