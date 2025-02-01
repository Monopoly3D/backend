from app.api.v1.exceptions.websocket import websocket_status
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class InternalServerError(WebSocketError):
    status_code = websocket_status.WS_4100_INTERNAL_ERROR
