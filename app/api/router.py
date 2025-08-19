from fastapi import APIRouter

from app.api.v1.router import v1_router, ws_v1_router

api_router: APIRouter = APIRouter(prefix="/api")
api_router.include_router(v1_router)

ws_router: APIRouter = APIRouter(prefix="/ws")
ws_router.include_router(ws_v1_router)
