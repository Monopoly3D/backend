from pydantic import BaseModel


class AuthenticationModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
