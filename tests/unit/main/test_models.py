from datetime import datetime, timedelta, timezone
from pytest import raises, mark
from fastapi.testclient import TestClient
from tortoise.exceptions import ValidationError
from ..models import BaseTestModel

pytestmark = mark.asyncio


async def test_create_invalid_base_model(client: TestClient):
    with raises(ValidationError):
        await BaseTestModel.create(name="Abyss")
    with raises(ValidationError):
        await BaseTestModel.create(name="@byys")
    with raises(ValidationError):
        await BaseTestModel.create(name="ąbyss")
    with raises(ValidationError):
        await BaseTestModel.create(name="ab")
    with raises(ValidationError):
        await BaseTestModel.create(name="twentyfivecharactersthere")


async def test_base_model_update(client: TestClient):
    model = await BaseTestModel.create(name="abyss")

    initial_created_at = model.created_at
    initial_modified_at = model.modified_at
    initial_now = datetime.now(timezone.utc)
    delta = timedelta(microseconds=500)

    assert model.name == "abyss"
    assert initial_now - initial_created_at < delta
    assert initial_now - initial_modified_at < delta

    model.name = "heaven"
    await model.save()

    updated_model = await BaseTestModel.get(name="heaven")

    assert initial_created_at == updated_model.created_at
    assert initial_modified_at < updated_model.modified_at
