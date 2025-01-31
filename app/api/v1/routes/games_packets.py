from app.api.v1.logging import logger
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.routes.packets import PacketsRouter
from config import Config

config: Config = Config(_env_file=".env")

games_packets_router = PacketsRouter(prefix="/games")


@games_packets_router.handle(ClientPingPacket)
async def on_client_ping(packet: ClientPingPacket):
    logger.info(f"Received message: {packet.request}")
    return ServerPingPacket("Message received!")
