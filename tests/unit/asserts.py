from app.models.base import NameMixin, TimestampMixin, AbstractModel
from .utils import is_uuid, is_date


def assert_pagination(json: dict, total: int, page: int = 1, size: int = 50):
    assert json["total"] == total
    assert len(json["items"]) == total
    assert json["page"] == page
    assert json["size"] == size


def assert_object_uuid(obj_json: dict, obj: AbstractModel):
    assert is_uuid(obj_json["uuid"])
    assert obj_json["uuid"] == str(obj.uuid)


def assert_object_name(obj_json: dict, obj: NameMixin):
    assert obj_json["name"] == obj.name


def assert_object_timestamps(obj_json: dict, obj: TimestampMixin):
    assert is_date(obj_json["created_at"])
    assert obj_json["created_at"] == obj.created_at.isoformat()
    assert is_date(obj_json["modified_at"])
    assert obj_json["modified_at"] == obj.modified_at.isoformat()


def assert_object(obj_json: dict, obj):
    assert_object_uuid(obj_json, obj)
    assert_object_name(obj_json, obj)
    assert_object_timestamps(obj_json, obj)
