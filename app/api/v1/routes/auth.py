import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.auth.authenticator import Authenticator
from app.api.v1.controllers.users import UsersController
from app.api.v1.models.response.authentication import AuthenticationModel
from app.api.v1.routes.games import games_router
from app.assets.user import User

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authorization"])


@games_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthenticationModel
)
async def register(
        username: str,
        users_controller: Annotated[UsersController, Depends(UsersController.dependency)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User = await users_controller.create_user(username=username)

    access_token: str = await asyncio.to_thread(
        authenticator.create_access_token,
        user_id=user.uuid,
        username=username
    )

    return AuthenticationModel(access_token=access_token)
