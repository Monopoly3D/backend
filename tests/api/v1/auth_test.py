from tests.conftest import client

test_user = {
    "username": "Plummy",
    "password": "test_password"
}


def test_registration():
    response = client.post(
        "http://127.0.0.1:8000/api/v1/auth/register",
        json=test_user
    )

    assert response.status_code == 201
    client.app_state["access_token"] = response.json()["access_token"]
    client.app_state["refresh_token"] = response.json()["refresh_token"]

    client.app_state["auth_headers"] = {"Authorization": f"Bearer {response.json()["access_token"]}"}


def test_login():
    response = client.post(
        "http://127.0.0.1:8000/api/v1/auth",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data=test_user
    )

    assert response.status_code == 202


def test_my_user():
    response = client.get(
        "http://127.0.0.1:8000/api/v1/auth",
        headers=client.app_state["auth_headers"]
    )

    assert response.status_code == 200

    client.app_state["user_id"] = response.json()["id"]


def test_refresh():
    response = client.post(
        "http://127.0.0.1:8000/api/v1/auth/refresh",
        headers={"refresh-token": client.app_state["refresh_token"]}
    )

    assert response.status_code == 202
    client.app_state["refresh_token"] = response.json()["refresh_token"]


def test_ticket():
    response = client.post(
        "http://127.0.0.1:8000/api/v1/auth/ticket",
        headers=client.app_state["auth_headers"]
    )

    assert response.status_code == 201
    client.app_state["ticket"] = response.json()["ticket"]
