from pydantic import BaseModel


class TicketModel(BaseModel):
    ticket: str
