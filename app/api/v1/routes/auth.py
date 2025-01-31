import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.controllers.users import UsersController
from app.api.v1.models.response.authentication import AuthenticationModel
from app.api.v1.models.response.ticket import TicketModel
from app.api.v1.security.authenticator import Authenticator
from app.assets.redis.user import User

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.post(
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
        user_id=user.user_id
    )

    return AuthenticationModel(access_token=access_token)


@auth_router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthenticationModel
)
async def login(
        username: str,
        users_controller: Annotated[UsersController, Depends(UsersController.dependency)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User = await users_controller.get_user_by_username(username=username)

    access_token: str = await asyncio.to_thread(
        authenticator.create_access_token,
        user_id=user.user_id
    )

    return AuthenticationModel(access_token=access_token)


@auth_router.post(
    "/ticket",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketModel
)
async def get_websocket_ticket(
        user: Annotated[User, Authenticator.get_user()],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> TicketModel:
    ticket: str = await asyncio.to_thread(
        authenticator.create_ticket,
        user_id=user.user_id
    )

    return TicketModel(ticket=ticket)
