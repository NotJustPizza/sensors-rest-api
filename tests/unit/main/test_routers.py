from typing import List
from fastapi.testclient import TestClient
from pytest import mark, fixture
from src.main.models import User
from ..utils import is_date, is_uuid, assert_json_pagination

pytestmark = mark.anyio


def assert_user_json(user_json: dict, user: User):
    assert is_uuid(user_json["uuid"])
    assert user_json["uuid"] == str(user.uuid)
    assert user_json["name"] == user.name
    assert user_json["email"] == user.email
    assert "password" not in user_json
    assert is_date(user_json["created_at"])
    assert user_json["created_at"] == user.created_at.isoformat()
    assert is_date(user_json["modified_at"])
    assert user_json["modified_at"] == user.modified_at.isoformat()


@fixture(scope="function", name="users")
async def populate_users():
    users_data = [
        {"name": "john", "email": "john@example.com"},
        {"name": "chad", "email": "chad@example.com"},
        {"name": "sarah", "email": "sarah@example.com"},
    ]
    users = []

    for user_data in users_data:
        user = await User.create(name=user_data["name"], email=user_data["email"])
        users.append(user)

    return users


async def test_index_page(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Welcome!"


async def test_retrieve_users(client: TestClient, users: List[User]):
    response = client.get("/users")
    json = response.json()

    assert response.status_code == 200
    assert_json_pagination(json, total=3)

    for i in range(json["total"]):
        assert_user_json(json["items"][i], users[i])


async def test_retrieve_user(client: TestClient, users: List[User]):
    user = users[0]

    response = client.get(f"/users/{user.uuid}")
    user_json = response.json()

    assert response.status_code == 200
    assert_user_json(user_json, user)


async def test_create_user(client: TestClient):
    user_data = {"name": "user", "email": "user@example.com", "password": "1111"}

    response = client.post("/users", json=user_data)
    user_json = response.json()
    user = await User.get(name=user_data["name"])

    assert response.status_code == 201
    assert_user_json(user_json, user)

    # Check if password was replaced by hash in database
    assert (
        user.password
        == "0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c"
    )
