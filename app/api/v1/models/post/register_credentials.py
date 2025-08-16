from pydantic import BaseModel, EmailStr


class RegisterCredentialsModel(BaseModel):
    username: str
    email: EmailStr
    password: str
