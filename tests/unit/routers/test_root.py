from fastapi.testclient import TestClient
from pytest import mark


@mark.anyio
async def test_index_page(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "Welcome!"
