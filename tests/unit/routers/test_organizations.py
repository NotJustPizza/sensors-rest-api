from fastapi.testclient import TestClient
from pytest import mark, fixture
from typing import List
from app.models.organization import Organization
from ..asserts import assert_json_pagination, assert_default_object_json
from ..utils import populate_objects

pytestmark = mark.anyio


def assert_org_json(org_json: dict, org: Organization):
    assert_default_object_json(org_json, org)


@fixture(scope="function", name="orgs")
async def populate_orgs():
    return await populate_objects(
        [{"name": "space"}, {"name": "miners"}, {"name": "pilots"}],
        Organization,
    )


async def test_retrieve_orgs(logged_client: TestClient, orgs: List[Organization]):
    response = logged_client.get("/organizations")
    assert response.status_code == 200

    json = response.json()
    assert_json_pagination(json, total=len(orgs))

    for i in range(len(orgs)):
        assert_org_json(json["items"][i], orgs[i])


async def test_retrieve_org(logged_client: TestClient, orgs: List[Organization]):
    org = orgs[0]
    response = logged_client.get(f"/organizations/{org.uuid}")
    assert response.status_code == 200

    org_json = response.json()
    assert_org_json(org_json, org)


async def test_create_org(logged_client: TestClient):
    org_data = {"name": "tribes"}

    response = logged_client.post("/organizations", json=org_data)
    assert response.status_code == 201

    org_json = response.json()
    org = await Organization.get(**org_data)

    assert_org_json(org_json, org)
