from typing import Dict, List

from pytest import raises
from tortoise.exceptions import DoesNotExist

from app.models import AbstractModel

from .utils import is_date, is_uuid


async def assert_object_matches_json(
    obj: AbstractModel, obj_json: dict, nested: bool = False, refresh: bool = False
):
    if refresh is True:
        await obj.refresh_from_db()

    for key, value in obj_json.items():
        assert (
            key != "password"
        ), "Passwords should never be returned in json responses."
        assert type(value) is not dict, "Dictionaries are not supported."

        # ManyToMany relationships
        if type(value) is list:
            assert (
                nested is not True
            ), "Multilevel ManyToMany relations are not supported."
            # Fetch nested objects from database
            await obj.fetch_related(key)
            nested_objects = getattr(obj, key)

            for index, nested_json in enumerate(value):
                assert (
                    type(nested_json) is dict
                ), "ManyToMany relation must consist of list of dictionaries."
                # Repeat same function for each nested object
                await assert_object_matches_json(
                    nested_objects[index], nested_json, nested=True
                )
            continue

        # Get value of object attribute with same name as in json
        obj_value = getattr(obj, key)

        # Ensure that uuids are actually uuids
        if key == "uuid" or key.endswith("_id"):
            assert is_uuid(value)
            # Uuid has to be converted to string fist
            obj_value = str(obj_value)

        # Ensure that *_at are valid dates
        if key.endswith("_at"):
            assert is_date(value)
            # Date has to be in iso format fist
            obj_value = obj_value.isoformat()

        # Ensure value matches object attribute
        assert (
            value == obj_value
        ), f"{value} from json doesn't match {obj_value} from object for key: {key}"


async def assert_objects_matches_jsons(
    objs: List[AbstractModel], obj_jsons: List[Dict]
):
    for obj_json in obj_jsons:
        obj = next(item for item in objs if str(item.uuid) == str(obj_json["uuid"]))
        await assert_object_matches_json(obj, obj_json)


async def assert_object_was_deleted(obj: AbstractModel):
    with raises(DoesNotExist):
        await obj.refresh_from_db()
