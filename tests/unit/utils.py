from uuid import UUID
from dateutil.parser import parse as parse_date


def is_uuid(data):
    try:
        UUID(str(data))
        return True
    except ValueError:
        raise ValueError(f"{data} is not UUID")


def is_date(data):
    try:
        parse_date(data, fuzzy=False)
        return True
    except ValueError:
        raise ValueError(f"{data} is not date")


def assert_json_pagination(json, total, page: int = 1, size: int = 50):
    assert json["total"] == total
    assert len(json["items"]) == total
    assert json["page"] == page
    assert json["size"] == size
