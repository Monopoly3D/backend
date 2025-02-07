from app.api.v1.exceptions.websocket import websocket_status
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class InternalServerError(WebSocketError):
    def __init__(self, detail: str, error: Exception) -> None:
        super().__init__(detail)
        self.error = error

    status_code = websocket_status.WS_4100_INTERNAL_ERROR
