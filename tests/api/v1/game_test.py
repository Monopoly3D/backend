from typing import Dict, Any

from tests.conftest import client


def test_create_game():
    response = client.post(
        "http://127.0.0.1:8000/api/v1/games",
        headers=client.app_state["auth_headers"]
    )

    assert response.status_code == 201
    client.app_state["game_id"] = response.json()["game_id"]


def test_websocket_auth():
    with client.websocket_connect("ws://127.0.0.1:8000/api/v1/games") as websocket:
        response: Dict[str, Any] = auth(websocket, client.app_state["ticket"])

        assert response["data"]["user_id"] == client.app_state["user_id"]


def test_websocket_ping():
    with client.websocket_connect("ws://127.0.0.1:8000/api/v1/games") as websocket:
        auth(websocket, client.app_state["ticket"])

        websocket.send_json(
            {
                "data": {},
                "meta": {
                    "tag": "ping",
                    "class": "client"
                }
            }
        )
        websocket.receive_json()


def test_websocket_join():
    with client.websocket_connect("ws://127.0.0.1:8000/api/v1/games") as websocket:
        auth(websocket, client.app_state["ticket"])

        websocket.send_json(
            {
                "data": {
                    "game_id": client.app_state["game_id"]
                },
                "meta": {
                    "tag": "player_join_game",
                    "class": "client"
                }
            }
        )
        print(websocket.receive_json())


def test_remove_game():
    response = client.delete(
        f"http://127.0.0.1:8000/api/v1/games/{client.app_state["game_id"]}",
        headers=client.app_state["auth_headers"]
    )

    assert response.status_code == 204


def auth(websocket, ticket):
    websocket.send_json(
        {
            "data": {
                "ticket": ticket
            },
            "meta": {
                "tag": "auth",
                "class": "client"
            }
        }
    )
    return websocket.receive_json()
