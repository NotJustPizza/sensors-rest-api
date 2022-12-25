from app.models.base import NameMixin, TimestampMixin, AbstractModel
from .utils import is_uuid, is_date


def assert_json_pagination(json: dict, total: int, page: int = 1, size: int = 50):
    assert json["total"] == total
    assert len(json["items"]) == total
    assert json["page"] == page
    assert json["size"] == size


def assert_uuid_in_object_json(obj_json: dict, obj: AbstractModel):
    assert is_uuid(obj_json["uuid"])
    assert obj_json["uuid"] == str(obj.uuid)


def assert_name_in_object_json(obj_json: dict, obj: NameMixin):
    assert obj_json["name"] == obj.name


def assert_timestamp_in_object_json(obj_json: dict, obj: TimestampMixin):
    assert is_date(obj_json["created_at"])
    assert obj_json["created_at"] == obj.created_at.isoformat()
    assert is_date(obj_json["modified_at"])
    assert obj_json["modified_at"] == obj.modified_at.isoformat()


def assert_default_object_json(obj_json: dict, obj):
    assert_uuid_in_object_json(obj_json, obj)
    assert_name_in_object_json(obj_json, obj)
    assert_timestamp_in_object_json(obj_json, obj)
