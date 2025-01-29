from starlette import status

from app.api.v1.exceptions.api_error import APIError


class InvalidPacketError(APIError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
