from asyncio import get_event_loop_policy
from typing import Generator
from pytest import fixture
from fastapi.testclient import TestClient
from tortoise.contrib.test import initializer, finalizer
from src.main.main import app, db_models


@fixture(scope="function")
def event_loop():
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()


@fixture(scope="function")
def client(request) -> Generator:
    db_models.append("tests.unit.models")
    initializer(db_models)
    with TestClient(app) as c:
        yield c
    request.addfinalizer(finalizer)
