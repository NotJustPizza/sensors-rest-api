from asyncio import AbstractEventLoop, BaseEventLoop, get_event_loop_policy
from secrets import token_hex
from typing import Iterator

from pytest import fixture
from tortoise.contrib.test import finalizer, initializer

from app.main import create_app, db_models
from app.models.user import User
from app.settings import Settings

from .utils import ApiTestClient, AuthContext

auth_pass: str = token_hex(32)
settings = Settings(
    custom_db_url="sqlite://:memory:", app_key=token_hex(32), admin_pass=auth_pass
)


@fixture(scope="function")
def anyio_backend():
    return "asyncio"


@fixture(scope="function")
def event_loop() -> Iterator[AbstractEventLoop]:
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@fixture(scope="function")
def client(request, event_loop: BaseEventLoop) -> Iterator[ApiTestClient]:
    app = create_app(settings)
    db_models.append("tests.unit.models.fixtures")
    initializer(db_models, loop=event_loop)
    with ApiTestClient(app) as c:
        yield c
    request.addfinalizer(finalizer)


@fixture(scope="function", params=[{"admin": True}, {"admin": False}])
async def auth_context(request, client: ApiTestClient) -> AuthContext:
    if request.param["admin"]:
        # Admin user is created at startup by application
        user = await User.get(email="admin@sensors-api.com")
    else:
        user = await User.create(
            email="auth@sensors-api.com", password=auth_pass, is_admin=False
        )
    return AuthContext(user=user, password=auth_pass)


@fixture(scope="function", params=[{"scope": "global"}])
async def auth_client(
    request, auth_context: AuthContext, client: ApiTestClient
) -> ApiTestClient:
    response = client.post(
        "/login",
        data={
            "username": auth_context.user.email,
            "password": auth_context.password,
            "scope": request.param["scope"],
        },
    )
    json = response.json()

    assert response.status_code == 200
    assert "access_token" in json
    assert json["token_type"] == "bearer"

    client.headers = {"Authorization": f"Bearer {json['access_token']}"}
    return client
