from asyncio import AbstractEventLoop, BaseEventLoop, get_event_loop_policy
from fastapi.testclient import TestClient
from tortoise.contrib.test import initializer, finalizer
from typing import Iterator
from pytest import fixture
from app.main import app, db_models


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
