from asyncio import Task
from typing import Annotated, Tuple, Dict
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from app.api.v1.exceptions.http.invalid_access_token import InvalidAccessTokenError
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_accept_auction import ClientPlayerAcceptAuctionPacket
from app.api.v1.packets.client.player_accept_casino import ClientPlayerAcceptCasinoPacket
from app.api.v1.packets.client.player_accept_prison import ClientPlayerAcceptPrisonPacket
from app.api.v1.packets.client.player_buy_field import ClientPlayerBuyFieldPacket
from app.api.v1.packets.client.player_buy_filiation import ClientPlayerBuyFiliationPacket
from app.api.v1.packets.client.player_buyout_field import ClientPlayerBuyoutFieldPacket
from app.api.v1.packets.client.player_join_game import ClientPlayerEnterGamePacket
from app.api.v1.packets.client.player_mortgage_field import ClientPlayerMortgageFieldPacket
from app.api.v1.packets.client.player_move import ClientPlayerMovePacket
from app.api.v1.packets.client.player_pay_prison import ClientPlayerPayPrisonPacket
from app.api.v1.packets.client.player_pay_rent import ClientPlayerPayRentPacket
from app.api.v1.packets.client.player_pay_tax import ClientPlayerPayTaxPacket
from app.api.v1.packets.client.player_put_field_for_auction import ClientPlayerPutFieldForAuctionPacket
from app.api.v1.packets.client.player_ready import ClientPlayerReadyPacket
from app.api.v1.packets.client.player_refuse_auction import ClientPlayerRefuseAuctionPacket
from app.api.v1.packets.client.player_refuse_casino import ClientPlayerRefuseCasinoPacket
from app.api.v1.packets.client.player_sell_filiation import ClientPlayerSellFiliationPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.routes.websocket.dependencies import WebSocketDependency
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.api.v1.security.authenticator import Authenticator
from app.assets.controllers.connections import ConnectionsController
from app.assets.controllers.redis.games import GamesController
from app.assets.enums.action_type import ActionType
from app.assets.exceptions.game_already_started import GameAlreadyStartedError
from app.assets.exceptions.game_max_players_reached import GameMaxPlayersReachedError
from app.assets.exceptions.game_not_found import GameNotFoundError
from app.assets.exceptions.player_already_in_game import PlayerAlreadyInGameError
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.database.models import User
from app.dependencies import database_websocket_session, games_controller_websocket

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.authenticate()
async def authenticate(
        websocket: WebSocket,
        session: Annotated[AsyncSession, Depends(database_websocket_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
        games_controller: Annotated[GamesController, Depends(games_controller_websocket)],
        connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)]
) -> None:
    await websocket.accept()

    try:
        join_packet: ClientPlayerEnterGamePacket = ClientPlayerEnterGamePacket.unpack(await websocket.receive_text())
    except InvalidPacketError:
        await websocket.close(3000, "Provided packet data is invalid")
        return

    try:
        ticket: Dict[str, str] = await authenticator.decode_game_ticket(join_packet.ticket)
    except InvalidAccessTokenError:
        await websocket.close(3000, "Provided ticket is invalid")
        return

    try:
        user_id: UUID = UUID(ticket["id"])
        game_id: UUID = UUID(ticket["game_id"])
    except ValueError | KeyError:
        await websocket.close(3000, "Provided ticket is invalid")
        return

    user: User = await session.scalar(
        select(User)
        .filter_by(id=user_id)
    )
    if user is None:
        await websocket.close(3000, "Provided ticket is invalid")
        return

    await connections.add_connection(websocket, user_id)

    game: Game = await games_controller.get_game(game_id, connections)

    if game is None:
        raise GameNotFoundError("Game with provided UUID was not found")
    if game.players.exists(user.id):
        raise PlayerAlreadyInGameError("You are already in game")
    if game.is_started:
        raise GameAlreadyStartedError("Game with provided UUID has already started")
    if game.players.size >= game.max_players:
        raise GameMaxPlayersReachedError("Game with provided UUID has too many players")

    player = Player(user.id, username=user.username)
    player.connection = websocket

    await game.players.join(player)
    await game.save()


@games_packets_router.handle(ClientPingPacket)
async def on_ping() -> ServerPingPacket:
    return ServerPingPacket()


@games_packets_router.handle(ClientPlayerEnterGamePacket)
async def on_player_join_game(
        websocket: WebSocket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(is_started=False, has_player=False)]
) -> None:
    if game.players.size >= game.max_players:
        raise GameMaxPlayersReachedError("Game with provided UUID has too many players")

    player = Player(user.id, username=user.username)
    player.connection = websocket

    await game.players.join(player)
    await game.save()


@games_packets_router.handle(ClientPlayerReadyPacket)
async def on_player_ready(
        packet: ClientPlayerReadyPacket,
        user: User,
        game: Annotated[Game, WebSocketDependency.get_game(is_started=False)]
) -> None:
    player: Player = game.players.get(user.id)

    await player.set_ready(packet.is_ready)
    await game.save()

    task: Task | None = game.get_start_task()

    if game.players.are_ready and task is None and game.players.size >= game.min_players:
        await game.start_countdown()
    elif not game.players.are_ready and task is not None:
        await game.stop_countdown()


@games_packets_router.handle(ClientPlayerMovePacket)
async def on_player_move(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    dices: Tuple[int, ...] = game.roll_dice()

    await player.move(dices)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyFieldPacket)
async def on_player_buy_field(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.BUY_FIELD, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buy_field()
    await game.save()


@games_packets_router.handle(ClientPlayerPutFieldForAuctionPacket)
async def on_player_put_field_for_auction(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.BUY_FIELD, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.put_field_on_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptAuctionPacket)
async def on_player_accept_auction(
        game: Annotated[Game, WebSocketDependency.get_game(
            action=ActionType.BUY_FIELD_ON_AUCTION,
            is_players_turn=True
        )]
) -> None:
    player: Player = game.players.current_on_auction

    await player.accept_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerRefuseAuctionPacket)
async def on_player_refuse_auction(
        game: Annotated[Game, WebSocketDependency.get_game(
            action=ActionType.BUY_FIELD_ON_AUCTION,
            is_players_turn=True
        )]
) -> None:
    player: Player = game.players.current_on_auction

    await player.refuse_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerPayRentPacket)
async def on_player_pay_rent(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.PAY_RENT, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.pay_rent()
    await game.save()


@games_packets_router.handle(ClientPlayerPayTaxPacket)
async def on_player_pay_tax(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.PAY_TAX, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.pay_tax()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptPrisonPacket)
async def on_player_accept_prison(
        game: Annotated[Game, WebSocketDependency.get_game(action=[ActionType.PRISON], is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.accept_prison()
    await game.save()


@games_packets_router.handle(ClientPlayerPayPrisonPacket)
async def on_player_pay_prison(
        game: Annotated[Game, WebSocketDependency.get_game(
            action=[ActionType.PRISON, ActionType.PAY_PRISON],
            is_players_turn=True
        )]
) -> None:
    player: Player = game.players.current

    await player.pay_prison()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptCasinoPacket)
async def on_player_accept_casino(
        packet: ClientPlayerAcceptCasinoPacket,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.CASINO, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.play_casino(packet.dices)
    await game.save()


@games_packets_router.handle(ClientPlayerRefuseCasinoPacket)
async def on_player_refuse_casino(
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.CASINO, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.refuse_casino()
    await game.save()


@games_packets_router.handle(ClientPlayerMortgageFieldPacket)
async def on_player_mortgage_field(
        packet: ClientPlayerMortgageFieldPacket,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.mortgage_field(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyoutFieldPacket)
async def on_player_buyout_field(
        packet: ClientPlayerBuyoutFieldPacket,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buyout_field(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyFiliationPacket)
async def on_player_buy_filiation(
        packet: ClientPlayerBuyFiliationPacket,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buy_filiation(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerSellFiliationPacket)
async def on_player_sell_filiation(
        packet: ClientPlayerSellFiliationPacket,
        game: Annotated[Game, WebSocketDependency.get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.sell_filiation(packet.field)
    await game.save()
