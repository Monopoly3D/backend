from uuid import UUID

from app.assets.controllers.base_s3 import S3Controller


class ProfilePicturesController(S3Controller):
    def bucket(self) -> str:
        return "profilepictures"

    async def upload_profile_picture(
            self,
            user_id: UUID,
            profile_picture: bytes
    ) -> None:
        await self.add(
            str(user_id),
            profile_picture
        )

    async def get_profile_picture_url(
            self,
            user_id: UUID
    ) -> str | None:
        return await self.url(str(user_id))

    async def delete_profile_picture(
            self,
            user_id: UUID
    ) -> None:
        await self.delete(str(user_id))
