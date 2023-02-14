from typing import List

from pytest import mark

from app.models import Dimension, Measure

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "dimensions:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 144], [{"admin": False}, 72]],
    indirect=["auth_context"],
)
async def test_retrieve_dimensions(
    auth_client: ApiTestClient, dimensions: List[Dimension], expected_total: int
):
    items = auth_client.api_list("/dimensions", expected_total)
    await assert_objects_matches_jsons(dimensions, items)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "dimensions:read"}],
    indirect=True,
)
async def test_retrieve_dimension(
    auth_client: ApiTestClient, dimensions: List[Dimension]
):
    dimension = dimensions[0]
    item = auth_client.api_get("/dimensions", dimension.uuid)
    await assert_object_matches_json(dimension, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "dimensions:write"}],
    indirect=True,
)
async def test_create_dimension(auth_client: ApiTestClient, measures: List[Measure]):
    data = {"value": 1, "unit": "metre", "measure_id": str(measures[0].uuid)}
    item = auth_client.api_create("/dimensions", data)
    dimension = await Dimension.get(**data)
    await assert_object_matches_json(dimension, item)
    await assert_object_matches_json(dimension, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "dimensions:write"}],
    indirect=True,
)
async def test_update_dimension(
    auth_client: ApiTestClient, dimensions: List[Dimension], measures: List[Measure]
):
    dimension = dimensions[0]
    data = {
        "value": 11.21,
        "unit": "seconds",
        "measure_id": str(measures[1].uuid),
    }
    item = auth_client.api_update("/dimensions", dimension.uuid, data)
    await assert_object_matches_json(dimension, item, refresh=True)
    await assert_object_matches_json(dimension, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "dimensions:write"}],
    indirect=True,
)
async def test_delete_dimension(
    auth_client: ApiTestClient, dimensions: List[Dimension]
):
    dimension = dimensions[0]
    auth_client.api_delete("/dimensions", dimension.uuid)
    await assert_object_was_deleted(dimension)
