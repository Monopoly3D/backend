from pydantic import BaseModel


class AuthenticationModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
