from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from starlette import status

from app.api.v1.enums.permission import Permission
from app.api.v1.models.response.profile_picture import ProfilePictureResponseModel
from app.api.v1.models.response.user import UserResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.api.v1.security.authorizer import Authorizer
from app.assets.s3.profile_pictures import ProfilePicturesController
from app.database.models import User
from app.dependencies import profile_pictures_controller_dependency

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
        pictures_controller: Annotated[ProfilePicturesController, Depends(profile_pictures_controller_dependency)]
) -> ProfilePictureResponseModel:
    url: str | None = await pictures_controller.get_profile_picture_url(user.id)
    return ProfilePictureResponseModel(url=url)


@users_router.post(
    "/profile_picture",
    response_model=ProfilePictureResponseModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Authorizer.has_permission(Permission.VIEW_OWN_USER)]
)
async def upload_profile_picture(
        user: Annotated[User, Authenticator.get_user()],
        pictures_controller: Annotated[ProfilePicturesController, Depends(profile_pictures_controller_dependency)],
        picture: UploadFile = File(),
) -> ProfilePictureResponseModel:
    await pictures_controller.upload_profile_picture(user.id, await picture.read())
    url: str | None = await pictures_controller.get_profile_picture_url(user.id)
    return ProfilePictureResponseModel(url=url)
