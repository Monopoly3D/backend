from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class InternalServerError(WebSocketError):
    status_code = 4100
