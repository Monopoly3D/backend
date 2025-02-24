from asyncio import Task
from typing import Annotated

from starlette.websockets import WebSocket

from app.api.v1.exceptions.websocket.field_already_owned import FieldAlreadyOwnedError
from app.api.v1.exceptions.websocket.field_not_found import FieldNotFoundError
from app.api.v1.exceptions.websocket.field_not_owned import FieldNotOwnedError
from app.api.v1.exceptions.websocket.game_not_awaiting_move import GameNotAwaitingMoveError
from app.api.v1.exceptions.websocket.invalid_field_type import InvalidFieldTypeError
from app.api.v1.exceptions.websocket.max_players import TooManyPlayersError
from app.api.v1.exceptions.websocket.not_enough_balance import NotEnoughBalanceError
from app.api.v1.exceptions.websocket.player_already_in_game import PlayerAlreadyInGameError
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_buy_field import ClientPlayerBuyFieldPacket
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGamePacket
from app.api.v1.packets.client.player_move import ClientPlayerMovePacket
from app.api.v1.packets.client.player_pay_rent import ClientPlayerPayRentPacket
from app.api.v1.packets.client.player_pay_tax import ClientPlayerPayTaxPacket
from app.api.v1.packets.client.player_ready import ClientPlayerReadyPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.api.v1.routes.websocket.dependencies import WebSocketDependency
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.assets.actions.pay_rent import PayRentAction
from app.assets.actions.pay_tax import PayTaxAction
from app.assets.enums.action_type import ActionType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.fields.tax import Tax
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPingPacket)
async def on_ping() -> ServerPingPacket:
    return ServerPingPacket()


@games_packets_router.handle(ClientPlayerJoinGamePacket)
async def on_player_join_game(
        websocket: WebSocket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(is_started=False, has_player=False)]
) -> None:
    if game.players.size >= game.max_players:
        raise TooManyPlayersError("Game with provided UUID has too many players")

    if game.players.exists(user.user_id):
        raise PlayerAlreadyInGameError("You are already in game")

    player = Player(user.user_id, username=user.username)
    player.connection = websocket

    game.players.add(player)
    await game.save()
    await game.send(ServerPlayerJoinGamePacket(game.game_id, player.player_id, player.username))


@games_packets_router.handle(ClientPlayerReadyPacket)
async def on_player_ready(
        packet: ClientPlayerReadyPacket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(is_started=False, has_player=True)]
) -> None:
    player: Player = game.players.get(user.user_id)
    player.is_ready = packet.is_ready

    await game.save()
    await game.send(ServerPlayerReadyPacket(game.game_id, player.player_id, packet.is_ready))

    task: Task | None = game.get_start_task()

    if game.players.are_ready and task is None and game.players.size >= game.min_players:
        await game.start_countdown()
    elif not game.players.are_ready and task is not None:
        await game.stop_countdown()


@games_packets_router.handle(ClientPlayerMovePacket)
async def on_player_move(
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE)]
) -> None:
    if game.players.get_by_move().player_id != user.user_id:
        raise GameNotAwaitingMoveError("Player is not awaited to move")

    await game.move_player()
    await game.save()


@games_packets_router.handle(ClientPlayerBuyFieldPacket)
async def on_player_buy_field(
        packet: ClientPlayerBuyFieldPacket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.BUY_FIELD)]
) -> None:
    player: Player | None = game.players.get_by_move()

    if player.player_id != user.user_id:
        raise GameNotAwaitingMoveError("Player is not awaited to buy field")

    field: Field | None = game.fields.get(packet.field)

    if field is None:
        raise FieldNotFoundError("Field with provided index was not found")

    if not isinstance(field, Company):
        raise InvalidFieldTypeError("Provided field is not a company")

    if field.owner_id is not None:
        raise FieldAlreadyOwnedError("Provided field is already owned")

    if field.cost > player.balance:
        raise NotEnoughBalanceError("Player has insufficient balance")

    await player.buy_field(field.field_id)
    await game.save()


@games_packets_router.handle(ClientPlayerPayRentPacket)
async def on_player_pay_rent(
        packet: ClientPlayerPayRentPacket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.PAY_RENT)]
) -> None:
    player: Player | None = game.players.get_by_move()

    if player.player_id != user.user_id:
        raise GameNotAwaitingMoveError("Player is not awaited to pay rent")

    field: Field | None = game.fields.get(packet.field)

    if field is None:
        raise FieldNotFoundError("Field with provided index was not found")

    if not isinstance(field, Company):
        raise InvalidFieldTypeError("Provided field is not a company")

    if field.owner_id is None:
        raise FieldNotOwnedError("Provided field is not owned")

    if field.owner_id == player.player_id:
        raise FieldAlreadyOwnedError("Provided field is already owned")

    action: PayRentAction = game.action

    if action.amount > player.balance:
        raise NotEnoughBalanceError("Player has insufficient balance")

    await player.pay_rent(field.field_id)
    await game.save()


@games_packets_router.handle(ClientPlayerPayTaxPacket)
async def on_player_pay_tax(
        packet: ClientPlayerPayTaxPacket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.PAY_TAX)]
) -> None:
    player: Player | None = game.players.get_by_move()

    if player.player_id != user.user_id:
        raise GameNotAwaitingMoveError("Player is not awaited to pay tax")

    field: Field | None = game.fields.get(packet.field)

    if field is None:
        raise FieldNotFoundError("Field with provided index was not found")

    if not isinstance(field, Tax):
        raise InvalidFieldTypeError("Provided field is not a tax field")

    action: PayTaxAction = game.action

    if action.amount > player.balance:
        raise NotEnoughBalanceError("Player has insufficient balance")

    await player.pay_tax()
    await game.save()
