from uuid import UUID

from pydantic import BaseModel


class GameResponseModel(BaseModel):
    id: UUID
    is_started: bool
