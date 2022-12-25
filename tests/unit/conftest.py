from asyncio import AbstractEventLoop, BaseEventLoop, get_event_loop_policy
from fastapi.testclient import TestClient
from tortoise.contrib.test import initializer, finalizer
from typing import Iterator
from pytest import fixture
from secrets import token_hex
import app.settings

# Workaround for db_url not working in tortoise initializer for pytest
# Ref: https://github.com/tortoise/tortoise-orm/issues/704
app.settings.get_settings = lambda: app.settings.Settings(
    custom_db_url="sqlite://:memory:", app_key=token_hex(32)
)

from app.main import db_models, app as test_app
from app.models.user import User
from .utils import AuthContext


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
def client(request, event_loop: BaseEventLoop) -> Iterator[TestClient]:
    db_models.append("tests.unit.models.fixtures")
    initializer(db_models, loop=event_loop)
    with TestClient(test_app) as c:
        yield c
    request.addfinalizer(finalizer)


@fixture(scope="function")
async def auth_context(client: TestClient) -> AuthContext:
    password = "abcd1234"

    user = User(name="user", email="auth@example.com", password=password)
    await user.save()

    return AuthContext(user=user, password=password)


@fixture(scope="function")
async def logged_client(auth_context: AuthContext, client: TestClient) -> TestClient:
    response = client.post(
        "/login",
        data={"username": auth_context.user.email, "password": auth_context.password},
    )
    json = response.json()

    assert response.status_code == 200
    assert "access_token" in json
    assert json["token_type"] == "bearer"

    client.headers = {"Authorization": f"Bearer {json['access_token']}"}
    return client
