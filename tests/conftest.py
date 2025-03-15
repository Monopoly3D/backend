import asyncio
import sys
from asyncio import AbstractEventLoop
from typing import AsyncGenerator

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.asgi import config, app
from app.database.database import Database
from app.dependencies import database_session, database_websocket_session

test_database: Database = Database.from_dsn(config.test_database_dsn.get_secret_value())

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def test_database_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_database.session_maker() as session:
        yield session


async def test_database_websocket_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_database.session_maker() as session:
        yield session


client = TestClient(app, base_url="http://localhost:8000")

app.state_database = test_database
app.state.test_database = test_database
app.dependency_overrides[database_session] = test_database_session
app.dependency_overrides[database_websocket_session] = test_database_websocket_session


def setup():
    alembic_cfg = AlembicConfig()

    alembic_cfg.set_main_option("script_location", "./migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", config.test_database_dsn.get_secret_value())
    command.upgrade(alembic_cfg, "heads")


async def async_teardown():
    async with test_database.engine.connect() as db:
        await db.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        await db.commit()


@pytest.fixture(scope="session", autouse=True)
def prepare():
    setup()
    yield
    asyncio.run(async_teardown())


@pytest.fixture(scope="session")
async def loop() -> AsyncGenerator[AbstractEventLoop, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[TestClient, None]:
    async with TestClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        yield ac
