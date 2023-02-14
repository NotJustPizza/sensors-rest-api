from typing import List

from pytest import mark

from app.models import User

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 6], [{"admin": False}, 1]],
    indirect=["auth_context"],
)
async def test_retrieve_users(
    auth_client: ApiTestClient, users: List[User], expected_total: int
):
    items = auth_client.api_list("/users", expected_total)
    await assert_objects_matches_jsons(users, items)


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:read"}], indirect=True
)
async def test_retrieve_user(auth_client: ApiTestClient, auth_user: User):
    item = auth_client.api_get("/users", auth_user.uuid)
    await assert_object_matches_json(auth_user, item)


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
@mark.parametrize("auth_context", [{"admin": True}], indirect=True)
async def test_create_user(auth_client: ApiTestClient):
    data = {"email": "seba@sensors-api.com", "password": "abcd1234"}
    item = auth_client.api_create("/users", data)
    user = await User.get(email=data["email"])
    await assert_object_matches_json(user, item)
    assert user.email == data["email"]
    # Check if password was replaced by hash in database
    assert user.password.startswith("$argon2id$v=19$m=65536,t=3,p=4$")


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_update_user(auth_client: ApiTestClient, auth_user: User):
    data = {"email": "miko@sensors-api.com"}
    item = auth_client.api_update("/users", auth_user.uuid, data)
    await assert_object_matches_json(auth_user, item, refresh=True)
    await assert_object_matches_json(auth_user, data)


@mark.parametrize(
    "auth_client", [{"scope": "global"}, {"scope": "users:write"}], indirect=True
)
async def test_delete_user(auth_client: ApiTestClient, auth_user: User):
    auth_client.api_delete("/users", auth_user.uuid)
    await assert_object_was_deleted(auth_user)
