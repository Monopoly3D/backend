from starlette import status

from app.api.v1.exceptions.api_error import APIError


class InvalidCredentialsError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
