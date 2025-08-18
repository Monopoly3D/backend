from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.v1.enums.permission import Permission
from app.api.v1.models.response.profile_picture import ProfilePictureResponseModel
from app.api.v1.models.response.user import UserResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.api.v1.security.authorizer import Authorizer
from app.database.models import User
from app.dependencies import database_session

users_router: APIRouter = APIRouter(prefix="/users", tags=["User"])


@users_router.get(
    "",
    response_model=UserResponseModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Authorizer.has_permission(Permission.VIEW_OWN_USER)]
)
async def my_user(
        user: Annotated[User, Authenticator.get_user()]
) -> User:
    return user


@users_router.get(
    "/profile_picture",
    response_model=ProfilePictureResponseModel,
    status_code=status.HTTP_200_OK,
    dependencies=[Authorizer.has_permission(Permission.VIEW_OWN_USER)]
)
async def profile_picture(
        user: Annotated[User, Authenticator.get_user()],
        session: Annotated[AsyncSession, Depends(database_session)],
) -> User:
    return user
