from dataclasses import dataclass
from uuid import UUID

from starlette.websockets import WebSocket


@dataclass
class Connection:
    websocket: WebSocket
    user_id: UUID
