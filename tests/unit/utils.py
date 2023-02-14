from copy import copy
from typing import Any, Dict, List, Type
from uuid import UUID

from dateutil.parser import parse as parse_date
from fastapi.testclient import TestClient

from app.models import AbstractModel, User


def is_uuid(data: Any) -> bool:
    try:
        UUID(str(data))
        return True
    except ValueError:
        raise ValueError(f"{data} is not UUID")


def is_date(data: Any) -> bool:
    try:
        parse_date(data, fuzzy=False)
        return True
    except ValueError:
        raise ValueError(f"{data} is not date")


async def populate_objects(
    data: List[Dict[str, str]], model: Type[AbstractModel]
) -> List:
    objs = []
    for args in data:
        obj = await model.create(**args)
        objs.append(obj)

    return objs


class AuthContext:
    user: User
    password: str

    def __init__(self, user, password):
        self.user = user
        self.password = password


class ApiTestClient(TestClient):
    def api_get_page(
        self, api_prefix: str, page: int, page_size: int, page_total: int, total: int
    ) -> Dict:
        response = self.get(api_prefix, params={"page": page})
        json, status_code = response.json(), response.status_code
        assert (
            status_code == 200
        ), f"Expected status code 200, got {status_code}. API returned: {json}"
        # Check that pagination is working correctly
        assert (
            json["total"] == total
        ), f"Total from json is: {json['total']}, expected: {total}"
        assert (
            len(json["items"]) == page_total
        ), f"Page total is: {json['items']}, expected: {page_total}"
        assert json["page"] == page
        assert json["size"] == page_size

        return json["items"]

    def api_list(self, api_prefix: str, expected_total: int) -> List[dict]:
        page = 1
        page_size = 50
        unprocessed_items = copy(expected_total)
        items: List[dict] = []

        while unprocessed_items > 0:
            if unprocessed_items >= page_size:
                page_total = page_size
            else:
                page_total = unprocessed_items
            items.extend(
                self.api_get_page(
                    api_prefix, page, page_size, page_total, expected_total
                )
            )
            page += 1
            unprocessed_items -= page_size

        assert (
            len(items) == expected_total
        ), f"Total is: {len(items)}, expected: {expected_total}."
        return items

    def api_get(self, api_prefix: str, obj_uuid: UUID) -> dict:
        response = self.get(f"{api_prefix}/{obj_uuid}")
        item, status_code = response.json(), response.status_code
        assert (
            status_code == 200
        ), f"Expected status code 200, got {status_code}. API returned: {item}"
        return item

    def api_create(self, api_prefix: str, data: dict) -> dict:
        response = self.post(f"{api_prefix}", json=data)
        item, status_code = response.json(), response.status_code
        assert (
            status_code == 201
        ), f"Expected status code 201, got {status_code}. API returned: {item}"
        return item

    def api_update(self, api_prefix: str, obj_uuid: UUID, data: dict) -> dict:
        response = self.post(f"{api_prefix}/{obj_uuid}", json=data)
        item, status_code = response.json(), response.status_code
        assert (
            status_code == 200
        ), f"Expected status code 200, got {status_code}. API returned: {item}"
        return item

    def api_delete(self, api_prefix: str, obj_uuid: UUID) -> None:
        response = self.delete(f"{api_prefix}/{obj_uuid}")
        status_code = response.status_code
        assert status_code == 204, f"Expected status code 204, got {status_code}."
