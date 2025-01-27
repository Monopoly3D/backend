from starlette import status


class APIError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
