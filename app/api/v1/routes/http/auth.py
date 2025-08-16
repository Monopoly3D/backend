from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import select, update, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.assets.email_creator import EmailCreator
from app.api.v1.enums.permission import Permission
from app.api.v1.exceptions.http.already_exists import AlreadyExistsError
from app.api.v1.exceptions.http.invalid_credentials import InvalidCredentialsError
from app.api.v1.exceptions.http.invalid_register_token import InvalidRegisterTokenError
from app.api.v1.exceptions.http.not_found import NotFoundError
from app.api.v1.models.post.login_credentials import LoginCredentialsModel
from app.api.v1.models.post.register_credentials import RegisterCredentialsModel
from app.api.v1.models.response.authentication import AuthenticationModel
from app.api.v1.models.response.ticket import TicketModel
from app.api.v1.models.response.user import UserResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.api.v1.security.authorizer import Authorizer
from app.database.models import User, UserRole, Role
from app.dependencies import database_session, no_reply_email_dependency, config_dependency
from config import Config

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authorization"])


@auth_router.get(
    "",
    response_model=UserResponseModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Authorizer.has_permission(Permission.VIEW_OWN_USER)]
)
async def my_user(
        user: Annotated[User, Authenticator.get_user()]
) -> User:
    return user


@auth_router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthenticationModel
)
async def login(
        response: Response,
        credentials: LoginCredentialsModel,
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    user: User | None = await session.scalar(
        select(User)
        .filter_by(username=credentials.username)
    )

    if user is None:
        user: User | None = await session.scalar(
            select(User)
            .filter_by(email=credentials.username)
        )

    if user is None:
        raise NotFoundError("User with provided credentials was not found")

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
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return AuthenticationModel(access_token=access_token)


@auth_router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED
)
async def register(
        credentials: RegisterCredentialsModel,
        session: Annotated[AsyncSession, Depends(database_session)],
        config: Annotated[Config, Depends(config_dependency)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)],
        email: Annotated[FastMail, Depends(no_reply_email_dependency)],
        background_tasks: BackgroundTasks
) -> None:
    user: User | None = await session.scalar(
        select(User)
        .filter(
            or_(
                User.username == credentials.username,
                User.email == credentials.email,
            )
        )
    )

    if user is not None:
        raise AlreadyExistsError("User with provided credentials already exists")

    register_token: str = await authenticator.create_register_token(
        credentials.username,
        credentials.email,
        await authenticator.hash_password(credentials.password)
    )

    background_tasks.add_task(
        email.send_message,
        EmailCreator.create_verification_message(
            credentials.email,
            verification_url=config.verification_url.format(register_token=register_token),
        ),
        template_name=None,
        html_template=None,
        plain_template=None
    )


@auth_router.post(
    "/verify",
    response_model=AuthenticationModel,
    status_code=status.HTTP_202_ACCEPTED
)
async def verify(
        response: Response,
        user: Annotated[User, Authenticator.get_register_user()],
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        raise InvalidRegisterTokenError("Provided register token has already been used")

    session.add(
        UserRole(
            user_id=user.id,
            role=Role.USER
        )
    )

    access_token: str = await authenticator.create_access_token(user.id)
    refresh_token: str = await authenticator.create_refresh_token(user.id)

    await session.execute(
        update(User)
        .filter_by(id=user.id)
        .values(refresh_token=refresh_token)
    )
    await session.commit()
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return AuthenticationModel(access_token=access_token)


@auth_router.post(
    "/refresh",
    response_model=AuthenticationModel,
    status_code=status.HTTP_202_ACCEPTED
)
async def refresh(
        request: Request,
        response: Response,
        session: Annotated[AsyncSession, Depends(database_session)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
) -> AuthenticationModel:
    refresh_token: str = request.cookies.get("refresh_token")
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
    response.set_cookie("refresh_token", refresh_token, httponly=True)

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
    ticket: str = await authenticator.create_ticket(user.id)

    return TicketModel(ticket=ticket)
