from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List
from app.models.user import User
from ..asserts import (
    assert_pagination,
    assert_object_uuid,
    assert_object_timestamps,
    assert_memberships,
)
from ..utils import AuthContext, populate_objects

pytestmark = mark.anyio


def assert_user_object(user_json: dict, user: User):
    assert_object_uuid(user_json, user)
    assert_object_timestamps(user_json, user)
    assert_memberships(user_json, user)
    assert "password" not in user_json


@fixture(scope="function", name="users")
async def populate_users(auth_context: AuthContext):
    # Auth user was already populated, so has to be added there
    users = [auth_context.user]
    users += await populate_objects(
        [
            {"email": "john@sensors-api.com"},
            {"email": "chad@sensors-api.com"},
            {"email": "sarah@sensors-api.com"},
        ],
        User,
    )

    return users


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 4], [{"admin": False}, 1]],
    indirect=["auth_context"],
)
async def test_retrieve_users(logged_client: TestClient, users: List[User], total: int):
    response = logged_client.get("/users")
    assert response.status_code == 200

    json = response.json()
    assert_pagination(json, total=total)

    for i in range(total):
        assert_user_object(json["items"][i], users[i])


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
async def test_retrieve_user(logged_client: TestClient, auth_context: AuthContext):
    response = logged_client.get(f"/users/{auth_context.user.uuid}")
    assert response.status_code == 200

    user_json = response.json()
    assert_user_object(user_json, auth_context.user)


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
@mark.parametrize("auth_context", [{"admin": True}], indirect=True)
async def test_create_user(logged_client: TestClient):
    user_data = {"email": "seba@sensors-api.com", "password": "abcd1234"}
    response = logged_client.post("/users", json=user_data)
    assert response.status_code == 201

    user_json = response.json()
    user = await User.get(email=user_data["email"])
    assert_user_object(user_json, user)

    # Check if password was replaced by hash in database
    assert user.password.startswith("$argon2id$v=19$m=65536,t=3,p=4$")


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_update_user(logged_client: TestClient, auth_context: AuthContext):
    user = auth_context.user
    user_data = {"email": "miko@sensors-api.com"}

    response = logged_client.post(f"/users/{user.uuid}", json=user_data)
    assert response.status_code == 200

    await user.refresh_from_db()
    assert user.email == user_data["email"]

    assert_user_object(response.json(), user)
