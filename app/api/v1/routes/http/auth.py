from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.v1.exceptions.http.already_exists import AlreadyExistsError
from app.api.v1.exceptions.http.invalid_credentials import InvalidCredentialsError
from app.api.v1.exceptions.http.not_found import NotFoundError
from app.api.v1.models.create.credentials import CredentialsModel
from app.api.v1.models.response.authentication import AuthenticationModel
from app.api.v1.models.response.ticket import TicketModel
from app.api.v1.models.response.user import UserResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.database.models import User
from app.dependencies import database_session

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.get(
    "",
    response_model=UserResponseModel,
    status_code=status.HTTP_200_OK
)
async def my_user(
        user: Annotated[User, Authenticator.get_user()]
) -> User:
    return user


@auth_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthenticationModel
)
async def login(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User | None = await session.scalar(
        select(User)
        .filter_by(username=credentials.username)
    )

    if user is None:
        raise NotFoundError("User with provided username was not found")

    if not await authenticator.verify_password(credentials.password, user.password_hash):
        raise InvalidCredentialsError("Provided credentials are invalid")

    access_token: str = await authenticator.create_access_token(user.id)
    refresh_token: str = await authenticator.create_refresh_token(user.id)

    await session.execute(
        update(User)
        .filter_by(id=user.id)
        .values(refresh_token=refresh_token)
    )
    await session.commit()

    return AuthenticationModel(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthenticationModel
)
async def register(
        credentials: CredentialsModel,
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User | None = await session.scalar(
        select(User)
        .filter_by(username=credentials.username)
    )

    if user is not None:
        raise AlreadyExistsError("User with provided username already exists")

    user: User = User(
        username=credentials.username,
        password_hash=await authenticator.hash_password(credentials.password)
    )
    session.add(user)
    await session.commit()

    access_token: str = await authenticator.create_access_token(user.id)
    refresh_token: str = await authenticator.create_refresh_token(user.id)

    await session.execute(
        update(User)
        .filter_by(id=user.id)
        .values(refresh_token=refresh_token)
    )
    await session.commit()

    return AuthenticationModel(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    "/refresh",
    response_model=AuthenticationModel,
    status_code=status.HTTP_202_ACCEPTED,
)
async def refresh(
        refresh_token: Annotated[str, Header()],
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User = await authenticator.verify_refresh_token(refresh_token, session)

    if user.refresh_token != refresh_token:
        raise InvalidCredentialsError("Provided credentials are invalid")

    access_token: str = await authenticator.create_access_token(user.id)
    refresh_token: str = await authenticator.create_refresh_token(user.id)

    await session.execute(
        update(User)
        .filter_by(id=user.id)
        .values(refresh_token=refresh_token)
    )
    await session.commit()

    return AuthenticationModel(
        access_token=access_token,
        refresh_token=refresh_token
    )


@auth_router.post(
    "/ticket",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketModel
)
async def get_websocket_ticket(
        user: Annotated[User, Authenticator.get_user()],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> TicketModel:
    ticket: str = await authenticator.create_ticket(user.id)

    return TicketModel(ticket=ticket)
