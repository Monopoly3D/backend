from app.api.v1.exceptions.websocket import websocket_status
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class NotAuthenticatedAddressError(WebSocketError):
    status_code = websocket_status.WS_4001_UNAUTHORIZED
