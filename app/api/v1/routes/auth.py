import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.controllers.users import UsersController
from app.api.v1.models.response.authentication import AuthenticationModel
from app.api.v1.security.authenticator import Authenticator
from app.assets.user import User
from app.dependencies import Dependency

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthenticationModel
)
async def register(
        username: str,
        users_controller: Annotated[UsersController, Depends(Dependency.users_controller)],
        authenticator: Annotated[Authenticator, Depends(Dependency.authenticator)]
) -> AuthenticationModel:
    user: User = await users_controller.create_user(username=username)

    access_token: str = await asyncio.to_thread(
        authenticator.create_access_token,
        user_id=user.user_id,
        username=username
    )

    return AuthenticationModel(access_token=access_token)
