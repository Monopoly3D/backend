from starlette import status

from app.api.v1.exceptions.api_error import APIError


class NotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
