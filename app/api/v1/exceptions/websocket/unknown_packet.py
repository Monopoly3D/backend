from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class UnknownPacketError(WebSocketError):
    status_code = 4001
