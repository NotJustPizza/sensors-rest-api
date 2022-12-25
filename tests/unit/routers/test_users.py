from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List, Union, Dict
from app.models.user import User
from ..utils import AuthContext, is_date, is_uuid, assert_json_pagination

pytestmark = mark.anyio


def assert_user_json(user_json: dict, user: User):
    assert is_uuid(user_json["uuid"])
    assert user_json["uuid"] == str(user.uuid)
    assert user_json["email"] == user.email
    assert "password" not in user_json
    assert is_date(user_json["created_at"])
    assert user_json["created_at"] == user.created_at.isoformat()
    assert is_date(user_json["modified_at"])
    assert user_json["modified_at"] == user.modified_at.isoformat()


@fixture(scope="function", name="users")
async def populate_users(auth_context: AuthContext):
    users_data = [
        {"email": "john@example.com"},
        {"email": "chad@example.com"},
        {"email": "sarah@example.com"},
    ]
    # Auth user was already populated, so has to be added there
    users = [auth_context.user]

    for user_data in users_data:
        user = await User.create(email=user_data["email"])
        users.append(user)

    return users


async def test_retrieve_users(logged_client: TestClient, users: List[User]):
    response = logged_client.get("/users")
    json = response.json()

    assert response.status_code == 200
    assert_json_pagination(json, total=4)

    for i in range(json["total"]):
        assert_user_json(json["items"][i], users[i])


async def test_retrieve_user(logged_client: TestClient, auth_context: AuthContext):
    response = logged_client.get(f"/users/{auth_context.user.uuid}")
    user_json = response.json()

    assert response.status_code == 200
    assert_user_json(user_json, auth_context.user)


async def test_create_user(logged_client: TestClient):
    user_data = {"email": "seba@example.com", "password": "abcd1234"}

    response = logged_client.post("/users", json=user_data)
    user_json = response.json()
    user = await User.get(email=user_data["email"])

    assert response.status_code == 201
    assert_user_json(user_json, user)

    # Check if password was replaced by hash in database
    assert user.password.startswith("$argon2id$v=19$m=65536,t=3,p=4$")
