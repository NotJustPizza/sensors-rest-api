from asyncio import AbstractEventLoop, BaseEventLoop, get_event_loop_policy
from fastapi.testclient import TestClient
from os import environ
from tortoise.contrib.test import initializer, finalizer
from typing import Iterator
from pytest import fixture
from app.main import create_app, db_models

# Workaround for db_url not working in tortoise initializer for pytest
# Ref: https://github.com/tortoise/tortoise-orm/issues/704
environ["CUSTOM_DB_URL"] = "sqlite://:memory:"
app = create_app()


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
    with TestClient(app) as c:
        yield c
    request.addfinalizer(finalizer)
