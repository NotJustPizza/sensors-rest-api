from typing import Dict, List, Type
from uuid import UUID

from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate
from tortoise.contrib.pydantic import PydanticModel as PydanticBaseModel
from tortoise.expressions import Q
from tortoise.functions import Count
from tortoise.models import Model as TortoiseBaseModel
from tortoise.queryset import QuerySetSingle

from ..dependencies import Auth
from ..exceptions import PermissionException
from ..models import User


def prepare_user_query(
    auth: Auth, perm_subqueries: List[Count]
) -> QuerySetSingle[User]:
    user_query = auth.user_query.only("is_admin")
    for index, subquery in enumerate(perm_subqueries):
        user_query = user_query.annotate(**{f"has_perm_{index}": subquery})
    return user_query


async def check_user_perms(user: User, perm_subqueries: List[Count]) -> None:
    """Requires user to be admin or have one of defined perms"""
    if user.is_admin:
        return
    for index in range(len(perm_subqueries)):
        if getattr(user, f"has_perm_{index}"):
            return
    raise PermissionException()


class APIResolver:
    """This class handles fetching and parsing models from orm"""

    PydanticModel: Type[PydanticBaseModel]
    TortoiseModel: Type[TortoiseBaseModel]

    def __init__(
        self,
        pydantic_model: Type[PydanticBaseModel],
        tortoise_model: Type[TortoiseBaseModel],
    ):
        self.PydanticModel = pydantic_model
        self.TortoiseModel = tortoise_model

    async def retrieve_page(self, auth: Auth, filter_subquery: Q) -> AbstractPage:
        user = await auth.user_query.only("is_admin")
        if user.is_admin:
            query = self.TortoiseModel.all()
        else:
            query = self.TortoiseModel.filter(filter_subquery)
        return await paginate(query, prefetch_related=True)

    async def retrieve_item(
        self, auth: Auth, uuid: UUID, read_perm_subqueries: List[Count]
    ) -> PydanticBaseModel:
        user = await prepare_user_query(auth, read_perm_subqueries)
        await check_user_perms(user, read_perm_subqueries)
        instance = await self.TortoiseModel.get(pk=uuid)
        return await self.PydanticModel.from_tortoise_orm(instance)

    async def create_item(
        self, auth: Auth, data: PydanticBaseModel, write_perm_subqueries: List[Count]
    ) -> PydanticBaseModel:
        user = await prepare_user_query(auth, write_perm_subqueries)
        await check_user_perms(user, write_perm_subqueries)
        instance = await self.TortoiseModel.create(**data.dict(exclude_unset=True))
        return await self.PydanticModel.from_tortoise_orm(instance)

    async def update_item(
        self,
        auth: Auth,
        uuid: UUID,
        data: PydanticBaseModel,
        write_perm_subqueries: List[Count],
        field_write_perm_subqueries: Dict[str, Count] | None = None,
    ) -> PydanticBaseModel:
        data = data.dict(exclude_unset=True)
        user_query = prepare_user_query(auth, write_perm_subqueries)

        if field_write_perm_subqueries is not None:
            for field, subquery in field_write_perm_subqueries.items():
                if field in data:
                    user_query = user_query.annotate(
                        **{f"has_write_perm_to_{field}": subquery}
                    )

        user = await user_query
        await check_user_perms(user, write_perm_subqueries)

        instance = await self.TortoiseModel.get(pk=uuid)
        for field, value in data.items():
            if field_write_perm_subqueries is not None:
                if field in field_write_perm_subqueries.keys():
                    # noinspection PyUnresolvedReferences
                    if not user.is_admin and not getattr(
                        user, f"has_write_perm_to_{field}"
                    ):
                        raise PermissionException(
                            f"Missing permissions to new {field}."
                        )
            setattr(instance, field, value)

        await instance.save()
        return await self.PydanticModel.from_tortoise_orm(instance)

    async def delete_item(
        self, auth: Auth, uuid: UUID, write_perm_subqueries: List[Count]
    ) -> None:
        user = await prepare_user_query(auth, write_perm_subqueries)
        await check_user_perms(user, write_perm_subqueries)
        instance = await self.TortoiseModel.get(pk=uuid).only("uuid")
        await instance.delete()
