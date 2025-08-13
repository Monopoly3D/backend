from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
