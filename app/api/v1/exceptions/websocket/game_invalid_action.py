from app.api.v1.exceptions.websocket import websocket_status
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class GameInvalidActionError(WebSocketError):
    status_code = websocket_status.WS_4000_BAD_REQUEST
