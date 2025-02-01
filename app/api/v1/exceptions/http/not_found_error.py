from starlette import status

from app.api.v1.exceptions.http.http_error import HTTPError


class NotFoundError(HTTPError):
    status_code = status.HTTP_404_NOT_FOUND
