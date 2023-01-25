from fastapi.testclient import TestClient
from pytest import mark

pytestmark = mark.anyio


async def test_healthcheck_action(client: TestClient):
    response = client.get("/actions/healthcheck")
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "healthy"
