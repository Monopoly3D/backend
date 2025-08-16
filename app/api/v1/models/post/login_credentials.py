from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class LoginCredentialsModel(BaseModel):
    username: Annotated[str, Form()]
    password: Annotated[str, Form()]
