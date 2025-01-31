from starlette import status

from app.api.v1.exceptions.api_error import APIError


class InvalidAccessTokenError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
