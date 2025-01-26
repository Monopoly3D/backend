from fastapi import FastAPI

from app.api.router import api_router
from config import Config

config: Config = Config(_env_file=".env")


app = FastAPI()
app.include_router(api_router)
