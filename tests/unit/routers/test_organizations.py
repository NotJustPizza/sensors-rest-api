from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List
from app.models.organization import Organization
from ..asserts import assert_pagination, assert_object
from ..utils import AuthContext, populate_objects

pytestmark = mark.anyio


def assert_org_object(org_json: dict, org: Organization):
    assert_object(org_json, org)


@fixture(scope="function", name="orgs")
async def populate_orgs(auth_context: AuthContext):
    orgs = await populate_objects(
        [{"name": "space"}, {"name": "miners"}, {"name": "pilots"}],
        Organization,
    )
    await orgs[0].members.add(auth_context.user)
    return orgs


@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 3], [{"admin": False}, 1]],
    indirect=["auth_context"],
)
async def test_retrieve_orgs(
    logged_client: TestClient, orgs: List[Organization], total: int
):
    response = logged_client.get("/organizations")
    assert response.status_code == 200

    json = response.json()
    assert_pagination(json, total=total)

    for i in range(total):
        assert_org_object(json["items"][i], orgs[i])


async def test_retrieve_org(logged_client: TestClient, orgs: List[Organization]):
    org = orgs[0]
    response = logged_client.get(f"/organizations/{org.uuid}")
    assert response.status_code == 200

    org_json = response.json()
    assert_org_object(org_json, org)


async def atest_create_org(logged_client: TestClient):
    org_data = {"name": "tribes"}

    response = logged_client.post("/organizations", json=org_data)
    assert response.status_code == 201

    org_json = response.json()
    org = await Organization.get(**org_data)

    assert_org_object(org_json, org)
