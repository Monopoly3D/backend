from starlette import status

from app.api.v1.exceptions.api_error import APIError


class AlreadyExistsError(APIError):
    status_code = status.HTTP_409_CONFLICT
