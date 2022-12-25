from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List
from app.models.user import User
from ..asserts import (
    assert_json_pagination,
    assert_uuid_in_object_json,
    assert_timestamp_in_object_json,
)
from ..utils import AuthContext, populate_objects

pytestmark = mark.anyio


def assert_user_json(user_json: dict, user: User):
    assert_uuid_in_object_json(user_json, user)
    assert_timestamp_in_object_json(user_json, user)
    assert "password" not in user_json


@fixture(scope="function", name="users")
async def populate_users(auth_context: AuthContext):
    # Auth user was already populated, so has to be added there
    users = [auth_context.user]
    users += await populate_objects(
        [
            {"email": "john@example.com"},
            {"email": "chad@example.com"},
            {"email": "sarah@example.com"},
        ],
        User,
    )

    return users


async def test_retrieve_users(logged_client: TestClient, users: List[User]):
    response = logged_client.get("/users")
    assert response.status_code == 200

    json = response.json()
    assert_json_pagination(json, total=len(users))

    for i in range(len(users)):
        assert_user_json(json["items"][i], users[i])


async def test_retrieve_user(logged_client: TestClient, auth_context: AuthContext):
    response = logged_client.get(f"/users/{auth_context.user.uuid}")
    assert response.status_code == 200

    user_json = response.json()
    assert_user_json(user_json, auth_context.user)


async def test_create_user(logged_client: TestClient):
    user_data = {"email": "seba@example.com", "password": "abcd1234"}

    response = logged_client.post("/users", json=user_data)
    assert response.status_code == 201

    user_json = response.json()
    user = await User.get(email=user_data["email"])
    assert_user_json(user_json, user)

    # Check if password was replaced by hash in database
    assert user.password.startswith("$argon2id$v=19$m=65536,t=3,p=4$")
