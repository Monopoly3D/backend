from pydantic import BaseModel


class GameTicketResponseModel(BaseModel):
    ticket: str
