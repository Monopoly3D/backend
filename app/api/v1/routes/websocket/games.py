from asyncio import Task
from typing import Annotated, Tuple

from starlette.websockets import WebSocket

from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.client.player_accept_auction import ClientPlayerAcceptAuctionPacket
from app.api.v1.packets.client.player_accept_casino import ClientPlayerAcceptCasinoPacket
from app.api.v1.packets.client.player_accept_prison import ClientPlayerAcceptPrisonPacket
from app.api.v1.packets.client.player_buy_field import ClientPlayerBuyFieldPacket
from app.api.v1.packets.client.player_buy_filiation import ClientPlayerBuyFiliationPacket
from app.api.v1.packets.client.player_buyout_field import ClientPlayerBuyoutFieldPacket
from app.api.v1.packets.client.player_join_game import ClientPlayerJoinGamePacket
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
from app.assets.enums.action_type import ActionType
from app.assets.exceptions.game_max_players_reached import GameMaxPlayersReachedError
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.database.models import User
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
