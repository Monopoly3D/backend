from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class InvalidPacketDataError(WebSocketError):
    status_code = 4000
