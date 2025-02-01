from starlette import status

from app.api.v1.exceptions.http.http_error import HTTPError


class AlreadyExistsError(HTTPError):
    status_code = status.HTTP_409_CONFLICT
