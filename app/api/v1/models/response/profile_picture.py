from pydantic import BaseModel


class ProfilePictureResponseModel(BaseModel):
    url: str | None = None
