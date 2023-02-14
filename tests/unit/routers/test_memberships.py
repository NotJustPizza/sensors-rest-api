from typing import List

from pytest import mark

from app.models import Membership, Organization, User

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "memberships:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 12], [{"admin": False}, 10]],
    indirect=["auth_context"],
)
async def test_retrieve_memberships(
    auth_client: ApiTestClient, memberships: List[Membership], expected_total: int
):
    items = auth_client.api_list("/memberships", expected_total)
    await assert_objects_matches_jsons(memberships, items)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "memberships:read"}],
    indirect=True,
)
async def test_retrieve_membership(
    auth_client: ApiTestClient, memberships: List[Membership]
):
    membership = memberships[0]
    item = auth_client.api_get("/memberships", membership.uuid)
    await assert_object_matches_json(membership, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "memberships:write"}],
    indirect=True,
)
async def test_create_membership(
    auth_client: ApiTestClient, organizations: List[Organization], users: List[User]
):
    data = {
        "is_admin": True,
        "organization_id": str(organizations[0].uuid),
        "user_id": str(users[-1].uuid),
    }
    item = auth_client.api_create("/memberships", data)
    membership = await Membership.get(**data)
    await assert_object_matches_json(membership, item)
    await assert_object_matches_json(membership, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "memberships:write"}],
    indirect=True,
)
async def test_update_membership(
    auth_client: ApiTestClient, memberships: List[Membership]
):
    membership = memberships[0]
    data = {
        "is_admin": False,
    }
    item = auth_client.api_update("/memberships", membership.uuid, data)
    await assert_object_matches_json(membership, item, refresh=True)
    await assert_object_matches_json(membership, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "memberships:write"}],
    indirect=True,
)
async def test_delete_membership(
    auth_client: ApiTestClient, memberships: List[Membership]
):
    membership = memberships[0]
    auth_client.api_delete("/memberships", membership.uuid)
    await assert_object_was_deleted(membership)
