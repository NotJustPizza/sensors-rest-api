from pytest import mark

from app.routers import resource_routers

from ..utils import ApiTestClient, AuthContext

pytestmark = mark.anyio


async def test_index_page(auth_client: ApiTestClient, auth_context: AuthContext):
    response = auth_client.get("/")
    assert response.status_code == 200
    assert response.json() == f"Welcome {auth_context.user.email}!"


prefixes = ["/users", "/organizations", "/projects"]


async def test_prefixes_match_routers():
    router_prefixes = []
    for router in resource_routers:
        router_prefixes.append(router.prefix)
    assert router_prefixes == prefixes


@mark.parametrize("prefix", prefixes)
async def test_resource_with_invalid_uuid(auth_client: ApiTestClient, prefix: str):
    response = auth_client.get(f"{prefix}/bd14c26e-a1db-47d6-9aa1-b8ea80ac0")
    json = response.json()
    assert response.status_code == 422
    assert json["detail"][0]["type"] == "type_error.uuid"
    assert json["detail"][0]["msg"] == "value is not a valid uuid"


@mark.parametrize("prefix", prefixes)
@mark.parametrize("auth_context", [{"admin": True}], indirect=True)
async def test_resource_with_inexistent_uuid_as_admin(
    auth_client: ApiTestClient, prefix: str
):
    response = auth_client.get(f"{prefix}/bd14c26e-a1db-47d6-9aa1-b8ea80ac008f")
    json = response.json()
    assert response.status_code == 404
    assert json["detail"] == "Object does not exist"


@mark.parametrize("prefix", prefixes)
@mark.parametrize("auth_context", [{"admin": False}], indirect=True)
async def test_resource_with_inexistent_uuid_as_user(
    auth_client: ApiTestClient, prefix: str
):
    response = auth_client.get(f"{prefix}/bd14c26e-a1db-47d6-9aa1-b8ea80ac008f")
    json = response.json()
    assert response.status_code == 403
    assert json["detail"].startswith("Missing")
    assert json["detail"].endswith("permissions.")
