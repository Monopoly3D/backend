from app.api.v1.exceptions.websocket.websocket_error import WebSocketError


class NotAuthenticatedAddressError(WebSocketError):
    status_code = 4002
