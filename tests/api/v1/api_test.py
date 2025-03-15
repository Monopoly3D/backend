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


def test_registration():
    global access_token
    global refresh_token
    global auth_headers

    response = client.post(
        "api/v1/auth/register",
        json=test_user
    )

    assert response.status_code == 201
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]

    auth_headers = {"Authorization": f"Bearer {access_token}"}


def test_login():
    response = client.post(
        "api/v1/auth",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data=test_user
    )

    assert response.status_code == 202


def test_my_user():
    global auth_headers

    response = client.get(
        "api/v1/auth",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_refresh():
    global refresh_token

    response = client.post(
        "api/v1/auth/refresh",
        headers={"refresh-token": refresh_token}
    )

    assert response.status_code == 202
    refresh_token = response.json()["refresh_token"]


def test_ticket():
    global auth_headers

    response = client.post(
        "api/v1/auth/ticket",
        headers=auth_headers
    )

    assert response.status_code == 201


def test_create_game():
    global game_id

    response = client.post(
        "api/v1/games",
        headers=auth_headers
    )

    assert response.status_code == 201
    game_id = response.json()["game_id"]
    print(game_id)


"""def test_remove_game():
    global game_id

    response = client.delete(
        f"api/v1/games/{game_id}",
        headers=auth_headers
    )

    assert response.status_code == 204"""
