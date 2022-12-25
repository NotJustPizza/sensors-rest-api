from dateutil.parser import parse as parse_date
from uuid import UUID
from typing import Any, Dict, List, Type
from app.models.base import AbstractModel
from app.models.user import User


class AuthContext:
    user: User
    password: str

    def __init__(self, user, password):
        self.user = user
        self.password = password


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
) -> List[AbstractModel]:
    objs = []
    for args in data:
        obj = await model.create(**args)
        objs.append(obj)

    return objs
