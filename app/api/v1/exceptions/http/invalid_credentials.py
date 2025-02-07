from starlette import status

from app.api.v1.exceptions.http.http_error import HTTPError


class InvalidCredentialsError(HTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
