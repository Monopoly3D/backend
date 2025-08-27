from asyncio import Task
from typing import Annotated, Tuple, Dict, List, Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from app.api.v1.exceptions.http.invalid_access_token import InvalidAccessTokenError
from app.api.v1.exceptions.websocket import websocket_status
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_accept_auction import ClientPlayerAcceptAuctionPacket
from app.api.v1.packets.client.player_accept_casino import ClientPlayerAcceptCasinoPacket
from app.api.v1.packets.client.player_accept_prison import ClientPlayerAcceptPrisonPacket
from app.api.v1.packets.client.player_buy_field import ClientPlayerBuyFieldPacket
from app.api.v1.packets.client.player_buy_filiation import ClientPlayerBuyFiliationPacket
from app.api.v1.packets.client.player_buyout_field import ClientPlayerBuyoutFieldPacket
from app.api.v1.packets.client.player_kick_player import ClientPlayerKickPlayerPacket
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
from app.api.v1.routes.websocket.packets import PacketsRouter
from app.api.v1.security.authenticator import Authenticator
from app.assets.enums.action_type import ActionType
from app.assets.exceptions import game_status
from app.assets.exceptions.game_already_started import GameAlreadyStartedError
from app.assets.exceptions.game_error import GameError
from app.assets.exceptions.game_invalid_action import GameInvalidActionError
from app.assets.exceptions.game_not_awaiting_move import GameNotAwaitingMoveError
from app.assets.exceptions.game_not_found import GameNotFoundError
from app.assets.exceptions.game_not_started import GameNotStartedError
from app.assets.objects.connection import Connection
from app.assets.objects.connections import Connections
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.redis.games import GamesController
from app.database.models import User
from app.dependencies import database_websocket_session, games_controller_websocket

games_packets_router = PacketsRouter(
    name="games_router",
    prefix="/games",
    exceptions=[GameError]
)


def get_game(
        *,
        is_started: bool | None = True,
        action: ActionType | List[ActionType] | None = None,
        is_players_turn: bool | None = False
) -> Callable:
    async def __get_game(
            connections: Connections,
            games_controller: GamesController,
            user: User
    ) -> Game:
        game: Game | None = await games_controller.get_game_by_player(user.id, connections=connections)

        if game is None:
            raise GameNotFoundError("Game with provided UUID was not found")

        if is_started is not None:
            if game.is_started and not is_started:
                raise GameAlreadyStartedError("Game with provided UUID has already started")
            if not game.is_started and is_started:
                raise GameNotStartedError("Game with provided UUID has not been started")

        if is_players_turn:
            player: Player | None = game.players.current

            if player is None or player.player_id != user.id:
                raise GameNotAwaitingMoveError("Player is not awaited to move")

        if action is not None:
            if isinstance(action, ActionType):
                action_list: List[ActionType] = [action]
            else:
                action_list = action
            if game.action.ACTION_TYPE not in action_list:
                raise GameInvalidActionError("Game with provided UUID awaits different action")

        return game

    return __get_game


@games_packets_router.authenticate()
async def authenticate(
        websocket: WebSocket,
        session: Annotated[AsyncSession, Depends(database_websocket_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
        games_controller: Annotated[GamesController, Depends(games_controller_websocket)],
        connections: Annotated[Connections, Depends(Connections.websocket_dependency)]
) -> None:
    connection = Connection(websocket, connections)
    await connection.accept()

    try:
        ticket: Dict[str, str] = await authenticator.decode_game_ticket(connection.query_params.get("ticket"))
    except InvalidAccessTokenError:
        await connection.close(
            websocket_status.WS_4001_UNAUTHORIZED,
            "Provided ticket is invalid"
        )
        return

    try:
        user_id: UUID = UUID(ticket["id"])
        game_id: UUID = UUID(ticket["game_id"])
    except ValueError | KeyError:
        await connection.close(
            websocket_status.WS_4001_UNAUTHORIZED,
            "Provided ticket is invalid"
        )
        return

    user: User = await session.scalar(
        select(User)
        .filter_by(id=user_id)
    )
    if user is None:
        await connection.close(
            websocket_status.WS_4001_UNAUTHORIZED,
            "Provided ticket is invalid"
        )
        return

    game: Game = await games_controller.get_game(game_id, connections=connections)

    if game is None:
        await connection.close(
            game_status.G_4201_GAME_NOT_FOUND,
            "Game was not found"
        )
        return
    if not game.players.exists(user.id) and game.players.size >= game.player_amount:
        await connection.close(
            game_status.G_4206_GAME_MAX_PLAYERS_REACHED,
            "Game with provided UUID has too many players"
        )
        return
    if not game.players.exists(user.id) and game.is_started:
        await connection.close(
            game_status.G_4302_PLAYER_NOT_IN_GAME,
            "You are not in game"
        )
        return

    await connections.add_connection(connection, user_id)

    await Player.new(
        user.id,
        user.username,
        is_host=user.id == game.host_id,
        game=game,
        connection=connection
    ).enter()

    await game.save()


@games_packets_router.handle(ClientPingPacket)
async def on_ping() -> ServerPingPacket:
    return ServerPingPacket()


@games_packets_router.handle(ClientPlayerReadyPacket)
async def on_player_ready(
        packet: ClientPlayerReadyPacket,
        user: User,
        game: Annotated[Game, get_game(is_started=False)]
) -> None:
    player: Player = game.players.get(user.id)

    await player.set_ready(packet.is_ready)
    await game.save()

    task: Task | None = game.get_start_task()

    if game.players.are_ready and task is None and game.players.size == game.player_amount:
        await game.start_countdown()
    elif not game.players.are_ready and task is not None:
        await game.stop_countdown()


@games_packets_router.handle(ClientPlayerKickPlayerPacket)
async def on_player_kick_player(
        packet: ClientPlayerKickPlayerPacket,
        user: User,
        game: Annotated[Game, get_game()]
) -> None:
    player: Player = game.players.get(user.id)
    player_to_kick: Player = game.players.get(packet.player_id)

    await player.kick(player_to_kick)


@games_packets_router.handle(ClientPlayerMovePacket)
async def on_player_move(
        game: Annotated[Game, get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    dices: Tuple[int, ...] = game.roll_dice()

    await player.move(dices)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyFieldPacket)
async def on_player_buy_field(
        game: Annotated[Game, get_game(action=ActionType.BUY_FIELD, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buy_field()
    await game.save()


@games_packets_router.handle(ClientPlayerPutFieldForAuctionPacket)
async def on_player_put_field_for_auction(
        game: Annotated[Game, get_game(action=ActionType.BUY_FIELD, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.put_field_on_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptAuctionPacket)
async def on_player_accept_auction(
        game: Annotated[
            Game,
            get_game(
                action=ActionType.BUY_FIELD_ON_AUCTION,
                is_players_turn=True
            )
        ]
) -> None:
    player: Player = game.players.current_on_auction

    await player.accept_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerRefuseAuctionPacket)
async def on_player_refuse_auction(
        game: Annotated[
            Game,
            get_game(
                action=ActionType.BUY_FIELD_ON_AUCTION,
                is_players_turn=True
            )
        ]
) -> None:
    player: Player = game.players.current_on_auction

    await player.refuse_auction()
    await game.save()


@games_packets_router.handle(ClientPlayerPayRentPacket)
async def on_player_pay_rent(
        game: Annotated[Game, get_game(action=ActionType.PAY_RENT, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.pay_rent()
    await game.save()


@games_packets_router.handle(ClientPlayerPayTaxPacket)
async def on_player_pay_tax(
        game: Annotated[Game, get_game(action=ActionType.PAY_TAX, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.pay_tax()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptPrisonPacket)
async def on_player_accept_prison(
        game: Annotated[Game, get_game(action=[ActionType.PRISON], is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.accept_prison()
    await game.save()


@games_packets_router.handle(ClientPlayerPayPrisonPacket)
async def on_player_pay_prison(
        game: Annotated[
            Game,
            get_game(
                action=[ActionType.PRISON, ActionType.PAY_PRISON],
                is_players_turn=True
            )
        ]
) -> None:
    player: Player = game.players.current

    await player.pay_prison()
    await game.save()


@games_packets_router.handle(ClientPlayerAcceptCasinoPacket)
async def on_player_accept_casino(
        packet: ClientPlayerAcceptCasinoPacket,
        game: Annotated[Game, get_game(action=ActionType.CASINO, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.play_casino(packet.dices)
    await game.save()


@games_packets_router.handle(ClientPlayerRefuseCasinoPacket)
async def on_player_refuse_casino(
        game: Annotated[Game, get_game(action=ActionType.CASINO, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.refuse_casino()
    await game.save()


@games_packets_router.handle(ClientPlayerMortgageFieldPacket)
async def on_player_mortgage_field(
        packet: ClientPlayerMortgageFieldPacket,
        game: Annotated[Game, get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.mortgage_field(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyoutFieldPacket)
async def on_player_buyout_field(
        packet: ClientPlayerBuyoutFieldPacket,
        game: Annotated[Game, get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buyout_field(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerBuyFiliationPacket)
async def on_player_buy_filiation(
        packet: ClientPlayerBuyFiliationPacket,
        game: Annotated[Game, get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.buy_filiation(packet.field)
    await game.save()


@games_packets_router.handle(ClientPlayerSellFiliationPacket)
async def on_player_sell_filiation(
        packet: ClientPlayerSellFiliationPacket,
        game: Annotated[Game, get_game(action=ActionType.MOVE, is_players_turn=True)]
) -> None:
    player: Player = game.players.current

    await player.sell_filiation(packet.field)
    await game.save()
