from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List
from app.models.organization import Organization, OrganizationMembership
from ..asserts import assert_pagination, assert_object
from ..utils import AuthContext, populate_objects

pytestmark = mark.anyio


def assert_organization_object(organization_json: dict, org: Organization):
    assert_object(organization_json, org)


@fixture(scope="function", name="organizations")
async def populate_organizations(auth_context: AuthContext):
    organizations = await populate_objects(
        [{"name": "space"}, {"name": "miners"}, {"name": "pilots"}],
        Organization,
    )
    await OrganizationMembership.create(
        user_id=auth_context.user.uuid,
        organization_id=organizations[0].uuid,
        is_admin=True,
    )
    return organizations


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "organizations:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 3], [{"admin": False}, 1]],
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
        assert_organization_object(json["items"][i], organizations[i])


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
    assert_organization_object(organization_json, organization)


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
    org = await Organization.get(**data)

    assert_organization_object(organization_json, org)


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

    assert_organization_object(response.json(), organization)
