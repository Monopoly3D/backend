import asyncio
import sys
from typing import AsyncGenerator

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.asgi import app, config
from app.database.database import Database
from app.dependencies import database_session

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


test_database: Database = Database.from_dsn(config.test_database_dsn.get_secret_value())


async def test_database_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_database.session_maker() as session:
        yield session


app.dependency_overrides[database_session] = test_database_session
app.state.session = test_database


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    alembic_cfg = AlembicConfig()

    alembic_cfg.set_main_option("script_location", "./migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", config.test_database_dsn.get_secret_value())
    command.upgrade(alembic_cfg, "heads")

    yield

    async with test_database.engine.connect() as db:
        await db.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        await db.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
