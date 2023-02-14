from typing import List

from pytest import mark

from app.models import Device, Project

from ..asserts import (
    assert_object_matches_json,
    assert_object_was_deleted,
    assert_objects_matches_jsons,
)
from ..utils import ApiTestClient

pytestmark = mark.anyio


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "devices:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 24], [{"admin": False}, 12]],
    indirect=["auth_context"],
)
async def test_retrieve_devices(
    auth_client: ApiTestClient, devices: List[Device], expected_total: int
):
    items = auth_client.api_list("/devices", expected_total)
    await assert_objects_matches_jsons(devices, items)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "devices:read"}],
    indirect=True,
)
async def test_retrieve_device(auth_client: ApiTestClient, devices: List[Device]):
    device = devices[0]
    item = auth_client.api_get("/devices", device.uuid)
    await assert_object_matches_json(device, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "devices:write"}],
    indirect=True,
)
async def test_create_device(auth_client: ApiTestClient, projects: List[Project]):
    data = {
        "name": "Detector",
        "type": "Raspberry",
        "project_id": str(projects[0].uuid),
    }
    item = auth_client.api_create("/devices", data)
    device = await Device.get(**data)
    await assert_object_matches_json(device, item)
    await assert_object_matches_json(device, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "devices:write"}],
    indirect=True,
)
async def test_update_device(
    auth_client: ApiTestClient, devices: List[Device], projects: List[Project]
):
    device, new_project = devices[0], projects[1]
    data = {
        "name": "Detector",
        "type": "Raspberry",
        "project_id": str(new_project.uuid),
    }
    item = auth_client.api_update("/devices", device.uuid, data)
    await assert_object_matches_json(device, item, refresh=True)
    await assert_object_matches_json(device, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "devices:write"}],
    indirect=True,
)
async def test_delete_device(auth_client: ApiTestClient, devices: List[Device]):
    device = devices[0]
    auth_client.api_delete("/devices", device.uuid)
    await assert_object_was_deleted(device)
