from pytest import mark
from typing import List
from app.models.user import User
from ..asserts import assert_object_matches_json, assert_object_was_deleted
from ..utils import AuthContext, ApiTestClient

pytestmark = mark.anyio
pytest_plugins = "tests.unit.routers.fixtures"


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 8], [{"admin": False}, 1]],
    indirect=["auth_context"],
)
async def test_retrieve_users(
    auth_client: ApiTestClient, users: List[User], expected_total: int
):
    items = auth_client.api_list("/users", expected_total)
    for i in range(expected_total):
        await assert_object_matches_json(users[i], items[i])


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
async def test_retrieve_user(auth_client: ApiTestClient, auth_context: AuthContext):
    user = auth_context.user
    item = auth_client.api_get("/users", user.uuid)
    await assert_object_matches_json(user, item)


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
@mark.parametrize("auth_context", [{"admin": True}], indirect=True)
async def test_create_user(auth_client: ApiTestClient):
    data = {"email": "seba@sensors-api.com", "password": "abcd1234"}
    item = auth_client.api_create("/users", data)
    user = await User.get(email=data["email"])
    await assert_object_matches_json(user, item)
    # Check if password was replaced by hash in database
    assert user.password.startswith("$argon2id$v=19$m=65536,t=3,p=4$")


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_update_user(auth_client: ApiTestClient, auth_context: AuthContext):
    user = auth_context.user
    data = {"email": "miko@sensors-api.com"}
    item = auth_client.api_update("/users", user.uuid, data)
    await assert_object_matches_json(user, item, refresh=True)
    await assert_object_matches_json(user, data)


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_delete_user(auth_client: ApiTestClient, auth_context: AuthContext):
    user = auth_context.user
    auth_client.api_delete("/users", user.uuid)
    await assert_object_was_deleted(user)
