from fastapi.testclient import TestClient
from pytest import mark, raises
from tortoise.exceptions import DoesNotExist
from typing import List
from app.models.user import User
from ..asserts import (
    assert_pagination,
    assert_object_uuid,
    assert_object_timestamps,
    assert_memberships,
)
from ..utils import AuthContext

pytestmark = mark.anyio
pytest_plugins = "tests.unit.routers.fixtures"


async def assert_user_object(user_json: dict, user: User):
    assert_object_uuid(user_json, user)
    assert_object_timestamps(user_json, user)
    await user.fetch_related("memberships")
    assert_memberships(user_json, user)
    assert "password" not in user_json


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 8], [{"admin": False}, 1]],
    indirect=["auth_context"],
)
async def test_retrieve_users(logged_client: TestClient, users: List[User], total: int):
    response = logged_client.get("/users")
    assert response.status_code == 200

    json = response.json()
    assert_pagination(json, total=total)

    for i in range(total):
        await assert_user_object(json["items"][i], users[i])


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
async def test_retrieve_user(logged_client: TestClient, auth_context: AuthContext):
    response = logged_client.get(f"/users/{auth_context.user.uuid}")
    assert response.status_code == 200

    user_json = response.json()
    await assert_user_object(user_json, auth_context.user)


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
    await assert_user_object(user_json, user)

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

    await assert_user_object(response.json(), user)


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_delete_user(logged_client: TestClient, auth_context: AuthContext):
    user = auth_context.user

    response = logged_client.delete(f"/users/{user.uuid}")
    assert response.status_code == 204

    with raises(DoesNotExist):
        await user.refresh_from_db()
