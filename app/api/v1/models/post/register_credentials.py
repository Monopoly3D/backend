from pydantic import BaseModel, EmailStr, Field


class RegisterCredentialsModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=40)
