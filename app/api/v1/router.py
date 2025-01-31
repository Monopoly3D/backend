from fastapi import APIRouter

from app.api.v1.routes.auth import auth_router
from app.api.v1.routes.games import games_router
from app.api.v1.routes.games_packets import games_packets_router

v1_router: APIRouter = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(games_router)

v1_router.include_router(games_packets_router)
