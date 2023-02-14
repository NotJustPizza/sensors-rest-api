from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models.dimension import Dimension
from ..pydantic import (
    DimensionCreatePydantic,
    DimensionOutPydantic,
    DimensionUpdatePydantic,
)
from .utils import APIResolver

router = APIRouter(prefix="/dimensions", tags=["dimensions"])
resolver = APIResolver(DimensionOutPydantic, Dimension)


@router.get("/", response_model=Page[DimensionOutPydantic])
async def retrieve_dimensions(auth: Auth = Depends(Auth(scope="dimensions:read"))):
    filter_subquery = Q(
        measure__device__project__organization__users__pk=auth.token.sub
    )
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=DimensionOutPydantic)
async def retrieve_dimension(
    uuid: UUID, auth: Auth = Depends(Auth(scope="dimensions:read"))
):
    read_perm_subquery = Count(
        "memberships__organization__projects__devices__measures__dimensions",
        _filter=Q(
            memberships__organization__projects__devices__measures__dimensions__pk=uuid
        ),
    )
    return await resolver.retrieve_item(auth, uuid, [read_perm_subquery])


@router.post("/", response_model=DimensionOutPydantic, status_code=201)
async def create_dimension(
    data: DimensionCreatePydantic, auth: Auth = Depends(Auth(scope="dimensions:write"))
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices__measures",
        _filter=Q(
            memberships__organization__projects__devices__measures__pk=data.measure_id,
            memberships__is_admin=True,
        ),
    )
    return await resolver.create_item(auth, data, [write_perm_subquery])


@router.post("/{uuid}", response_model=DimensionOutPydantic)
async def update_dimension(
    uuid: UUID,
    data: DimensionUpdatePydantic,
    auth: Auth = Depends(Auth(scope="dimensions:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices__measures__dimensions",
        _filter=Q(
            memberships__organization__projects__devices__measures__dimensions__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    field_write_perm_subqueries = {
        "measure_id": Count(
            "memberships__organization__projects__devices__measures",
            _filter=Q(
                memberships__organization__projects__devices__measures__pk=data.measure_id,
                memberships__is_admin=True,
            ),
        )
    }
    return await resolver.update_item(
        auth, uuid, data, [write_perm_subquery], field_write_perm_subqueries
    )


@router.delete("/{uuid}", status_code=204)
async def delete_dimension(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="dimensions:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices__measures__dimensions",
        _filter=Q(
            memberships__organization__projects__devices__measures__dimensions__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    return await resolver.delete_item(auth, uuid, [write_perm_subquery])
