from typing import List

from pytest import mark

from app.models import Device, Measure

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "measures:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 72], [{"admin": False}, 36]],
    indirect=["auth_context"],
)
async def test_retrieve_measures(
    auth_client: ApiTestClient, measures: List[Measure], expected_total: int
):
    items = auth_client.api_list("/measures", expected_total)
    await assert_objects_matches_jsons(measures, items)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "measures:read"}],
    indirect=True,
)
async def test_retrieve_measure(auth_client: ApiTestClient, measures: List[Measure]):
    measure = measures[0]
    item = auth_client.api_get("/measures", measure.uuid)
    await assert_object_matches_json(measure, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "measures:write"}],
    indirect=True,
)
async def test_create_measure(auth_client: ApiTestClient, devices: List[Device]):
    data = {
        "measured_at": "2010-01-03T14:16:17+00:00",
        "device_id": str(devices[0].uuid),
    }
    item = auth_client.api_create("/measures", data)
    measure = await Measure.get(pk=item["uuid"])
    await assert_object_matches_json(measure, item)
    await assert_object_matches_json(measure, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "measures:write"}],
    indirect=True,
)
async def test_update_measure(
    auth_client: ApiTestClient,
    measures: List[Measure],
    devices: List[Device],
):
    measure = measures[0]
    data = {
        "measured_at": "2021-12-01T16:04:32+00:00",
        "device_id": str(devices[1].uuid),
    }
    item = auth_client.api_update("/measures", measure.uuid, data)
    await assert_object_matches_json(measure, item, refresh=True)
    await assert_object_matches_json(measure, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "measures:write"}],
    indirect=True,
)
async def test_delete_measure(auth_client: ApiTestClient, measures: List[Measure]):
    measure = measures[0]
    auth_client.api_delete("/measures", measure.uuid)
    await assert_object_was_deleted(measure)
