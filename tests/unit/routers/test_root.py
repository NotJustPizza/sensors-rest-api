from fastapi.testclient import TestClient
from pytest import mark


pytestmark = mark.anyio


async def test_index_page(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Welcome!"


prefixes = ["/users"]


@mark.parametrize("prefix", prefixes)
async def test_resource_with_invalid_uuid(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/bd14c26e-a1db-47d6-9aa1-b8ea80ac0")
    json = response.json()

    assert response.status_code == 422
    assert json["detail"][0]["type"] == "type_error.uuid"
    assert json["detail"][0]["msg"] == "value is not a valid uuid"


@mark.parametrize("prefix", prefixes)
async def test_resource_with_inexistent_uuid(client: TestClient, prefix: str):
    response = client.get(f"{prefix}/bd14c26e-a1db-47d6-9aa1-b8ea80ac008f")
    json = response.json()

    assert response.status_code == 404
    assert json["detail"] == "Object does not exist"
