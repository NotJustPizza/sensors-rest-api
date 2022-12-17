from typing import List
from fastapi.testclient import TestClient
from pytest import mark, fixture
from src.main.models import User
from ..utils import is_date, is_uuid

pytestmark = mark.anyio


def assert_user_json(user_json: dict, user: User):
    assert is_uuid(user_json["uuid"])
    assert user_json["uuid"] == str(user.uuid)
    assert user_json["name"] == user.name
    assert is_date(user_json["created_at"])
    assert user_json["created_at"] == user.created_at.isoformat()
    assert is_date(user_json["modified_at"])
    assert user_json["modified_at"] == user.modified_at.isoformat()
    return True


@fixture(scope="function", name="users")
async def populate_users():
    user_names = ["john", "chad", "sarah"]
    users = []

    for user_name in user_names:
        user = await User.create(name=user_name)
        users.append(user)

    return users


async def test_index_page(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Welcome!"


async def test_retrieve_users(client: TestClient, users: List[User]):
    response = client.get("/users")
    users_json = response.json()

    assert response.status_code == 200

    for i, user_json in enumerate(users_json):
        assert assert_user_json(users_json[i], users[i])


async def test_retrieve_user(client: TestClient, users: List[User]):
    user = users[0]

    response = client.get(f"/users/{user.uuid}")
    user_json = response.json()

    assert response.status_code == 200
    assert assert_user_json(user_json, user)


async def test_create_user(client: TestClient):
    response = client.post("/users", json={"name": "user"})
    user_json = response.json()
    user = await User.get(name="user")

    assert response.status_code == 201
    assert assert_user_json(user_json, user)
