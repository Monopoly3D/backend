from starlette import status

from app.api.v1.exceptions.http.http_error import HTTPError


class InvalidPacketError(HTTPError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
