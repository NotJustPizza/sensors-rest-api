from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models.measure import Measure
from ..pydantic import MeasureCreatePydantic, MeasureOutPydantic, MeasureUpdatePydantic
from .utils import APIResolver

router = APIRouter(prefix="/measures", tags=["measures"])
resolver = APIResolver(MeasureOutPydantic, Measure)


@router.get("/", response_model=Page[MeasureOutPydantic])
async def retrieve_measures(auth: Auth = Depends(Auth(scope="measures:read"))):
    filter_subquery = Q(device__project__organization__users__pk=auth.token.sub)
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=MeasureOutPydantic)
async def retrieve_measure(
    uuid: UUID, auth: Auth = Depends(Auth(scope="measures:read"))
):
    read_perm_subquery = Count(
        "memberships__organization__projects__devices__measures",
        _filter=Q(memberships__organization__projects__devices__measures__pk=uuid),
    )
    return await resolver.retrieve_item(auth, uuid, [read_perm_subquery])


@router.post("/", response_model=MeasureOutPydantic, status_code=201)
async def create_measure(
    data: MeasureCreatePydantic, auth: Auth = Depends(Auth(scope="measures:write"))
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices",
        _filter=Q(
            memberships__organization__projects__devices__pk=data.device_id,
            memberships__is_admin=True,
        ),
    )
    return await resolver.create_item(auth, data, [write_perm_subquery])


@router.post("/{uuid}", response_model=MeasureOutPydantic)
async def update_measure(
    uuid: UUID,
    data: MeasureUpdatePydantic,
    auth: Auth = Depends(Auth(scope="measures:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices__measures",
        _filter=Q(
            memberships__organization__projects__devices__measures__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    field_write_perm_subqueries = {
        "device_id": Count(
            "memberships__organization__projects__devices",
            _filter=Q(
                memberships__organization__projects__devices__pk=data.device_id,
                memberships__is_admin=True,
            ),
        )
    }
    return await resolver.update_item(
        auth, uuid, data, [write_perm_subquery], field_write_perm_subqueries
    )


@router.delete("/{uuid}", status_code=204)
async def delete_measure(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="measures:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices__measures",
        _filter=Q(
            memberships__organization__projects__devices__measures__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    return await resolver.delete_item(auth, uuid, [write_perm_subquery])
