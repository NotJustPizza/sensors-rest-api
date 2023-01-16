from dateutil.parser import parse as parse_date
from fastapi.testclient import TestClient
from httpx import Response
from uuid import UUID
from typing import Any, Dict, List, Type
from app.models.base import AbstractModel
from app.models.user import User


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
    def api_list(
        self,
        api_prefix: str,
        expected_total: int,
    ) -> List[dict]:
        response = self.get(api_prefix)
        json, status_code = response.json(), response.status_code
        assert (
            status_code == 200
        ), f"Expected status code 200, got {status_code}. API returned: {json}"
        # Check that pagination is working correctly
        assert json["total"] == expected_total
        assert len(json["items"]) == expected_total
        assert json["page"] == 1
        assert json["size"] == 50

        return json["items"]

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
