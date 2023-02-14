from typing import List

from pytest import mark

from app.models import Organization

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "organizations:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 4], [{"admin": False}, 2]],
    indirect=["auth_context"],
)
async def test_retrieve_organizations(
    auth_client: ApiTestClient,
    organizations: List[Organization],
    expected_total: int,
):
    items = auth_client.api_list("/organizations", expected_total)
    await assert_objects_matches_jsons(organizations, items)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "organizations:read"}],
    indirect=True,
)
async def test_retrieve_organization(
    auth_client: ApiTestClient, organizations: List[Organization]
):
    organization = organizations[0]
    item = auth_client.api_get("/organizations", organization.uuid)
    await assert_object_matches_json(organization, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_create_organization(auth_client: ApiTestClient):
    data = {"name": "tribes"}
    item = auth_client.api_create("/organizations", data)
    organization = await Organization.get(**data)
    await assert_object_matches_json(organization, item)
    await assert_object_matches_json(organization, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_update_organization(
    auth_client: ApiTestClient, organizations: List[Organization]
):
    organization = organizations[0]
    data = {"name": "tribes"}
    item = auth_client.api_update("/organizations", organization.uuid, data)
    await assert_object_matches_json(organization, item, refresh=True)
    await assert_object_matches_json(organization, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_delete_organization(
    auth_client: ApiTestClient, organizations: List[Organization]
):
    organization = organizations[0]
    auth_client.api_delete("/organizations", organization.uuid)
    await assert_object_was_deleted(organization)
