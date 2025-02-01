from app.api.v1.exceptions.websocket import websocket_status


class WebSocketError(Exception):
    status_code = websocket_status.WS_4000_BAD_REQUEST
