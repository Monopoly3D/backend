import pytest
from aiohttp import ClientSession
from starlette.responses import Response

from tests.conftest import client

test_user = {
    "username": "Plummy",
    "password": "test_password"
}

access_token: str = ""
refresh_token: str = ""
ticket: str = ""

game_id: str = ""

auth_headers = {}


def test_registration() -> None:
    global access_token
    global refresh_token
    global auth_headers

    response: Response = client.post(
        "api/v1/auth/register",
        json=test_user
    )

    assert response.status_code == 201

"""
@pytest.mark.asyncio(loop_scope="session")
async def test_login() -> None:
    global access_token

    async with ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:8000/api/v1/auth",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=test_user
        ) as response:
            assert response.status == 202


@pytest.mark.asyncio(loop_scope="session")
async def test_my_user() -> None:
    global auth_headers

    async with ClientSession() as session:
        async with session.get(
            "http://127.0.0.1:8000/api/v1/auth",
            headers=auth_headers
        ) as response:
            assert response.status == 200
            assert (await response.json())["username"] == test_user["username"]


@pytest.mark.asyncio(loop_scope="session")
async def test_refresh() -> None:
    global refresh_token

    async with ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:8000/api/v1/auth/refresh",
            headers={"refresh-token": refresh_token}
        ) as response:
            assert response.status == 202


@pytest.mark.asyncio(loop_scope="session")
async def test_ticket() -> None:
    global auth_headers
    global ticket

    async with ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:8000/api/v1/auth/ticket",
            headers=auth_headers
        ) as response:
            assert response.status == 201
            ticket = (await response.json())["ticket"]
            print(ticket)


@pytest.mark.asyncio(loop_scope="session")
async def test_game_creation() -> None:
    global auth_headers
    global game_id

    async with ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:8000/api/v1/games",
            headers=auth_headers
        ) as response:
            assert response.status == 201
            game_id = (await response.json())["game_id"]
"""