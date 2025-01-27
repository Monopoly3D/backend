from fastapi import APIRouter
from starlette import status

games_router: APIRouter = APIRouter(prefix="/games", tags=["Games"])


@games_router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
async def create_game() -> None:
    pass
