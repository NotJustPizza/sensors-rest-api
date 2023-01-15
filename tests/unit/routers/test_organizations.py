from fastapi.testclient import TestClient
from pytest import mark, raises
from tortoise.exceptions import DoesNotExist
from typing import List
from app.models.organization import Organization
from ..asserts import assert_pagination, assert_object, assert_memberships

pytestmark = mark.anyio
pytest_plugins = "tests.unit.routers.fixtures"


async def assert_organization_object(
    organization_json: dict, organization: Organization
):
    assert_object(organization_json, organization)
    await organization.fetch_related("memberships")
    assert_memberships(organization_json, organization)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 4], [{"admin": False}, 2]],
    indirect=["auth_context"],
)
async def test_retrieve_organizations(
    logged_client: TestClient, organizations: List[Organization], total: int
):
    response = logged_client.get("/organizations")
    assert response.status_code == 200

    json = response.json()
    assert_pagination(json, total=total)

    for i in range(total):
        await assert_organization_object(json["items"][i], organizations[i])


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:read"}],
    indirect=True,
)
async def test_retrieve_organization(
    logged_client: TestClient, organizations: List[Organization]
):
    organization = organizations[0]
    response = logged_client.get(f"/organizations/{organization.uuid}")
    assert response.status_code == 200

    organization_json = response.json()
    await assert_organization_object(organization_json, organization)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_create_organization(logged_client: TestClient):
    data = {"name": "tribes"}

    response = logged_client.post("/organizations", json=data)
    assert response.status_code == 201

    organization_json = response.json()
    organization = await Organization.get(**data)

    await assert_organization_object(organization_json, organization)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_update_organization(
    logged_client: TestClient, organizations: List[Organization]
):
    organization = organizations[0]
    organization_data = {"name": "tribes"}

    response = logged_client.post(
        f"/organizations/{organization.uuid}", json=organization_data
    )
    assert response.status_code == 200

    await organization.refresh_from_db()
    assert organization.name == organization_data["name"]

    await assert_organization_object(response.json(), organization)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:write"}],
    indirect=True,
)
async def test_delete_organization(
    logged_client: TestClient, organizations: List[Organization]
):
    organization = organizations[0]

    response = logged_client.delete(f"/organizations/{organization.uuid}")
    assert response.status_code == 204

    with raises(DoesNotExist):
        await organization.refresh_from_db()
