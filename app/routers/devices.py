from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models.device import Device
from ..pydantic import DeviceCreatePydantic, DeviceOutPydantic, DeviceUpdatePydantic
from .utils import APIResolver

router = APIRouter(prefix="/devices", tags=["devices"])
resolver = APIResolver(DeviceOutPydantic, Device)


@router.get("/", response_model=Page[DeviceOutPydantic])
async def retrieve_devices(auth: Auth = Depends(Auth(scope="devices:read"))):
    filter_subquery = Q(project__organization__users__pk=auth.token.sub)
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=DeviceOutPydantic)
async def retrieve_device(uuid: UUID, auth: Auth = Depends(Auth(scope="devices:read"))):
    read_perm_subquery = Count(
        "memberships__organization__projects__devices",
        _filter=Q(memberships__organization__projects__devices__pk=uuid),
    )
    return await resolver.retrieve_item(auth, uuid, [read_perm_subquery])


@router.post("/", response_model=DeviceOutPydantic, status_code=201)
async def create_device(
    data: DeviceCreatePydantic, auth: Auth = Depends(Auth(scope="devices:write"))
):
    write_perm_subquery = Count(
        "memberships__organization__projects",
        _filter=Q(
            memberships__organization__projects__pk=data.project_id,
            memberships__is_admin=True,
        ),
    )
    return await resolver.create_item(auth, data, [write_perm_subquery])


@router.post("/{uuid}", response_model=DeviceOutPydantic)
async def update_device(
    uuid: UUID,
    data: DeviceUpdatePydantic,
    auth: Auth = Depends(Auth(scope="devices:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices",
        _filter=Q(
            memberships__organization__projects__devices__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    field_write_perm_subqueries = {
        "project_id": Count(
            "memberships__organization__projects",
            _filter=Q(
                memberships__organization__projects__pk=data.project_id,
                memberships__is_admin=True,
            ),
        )
    }
    return await resolver.update_item(
        auth, uuid, data, [write_perm_subquery], field_write_perm_subqueries
    )


@router.delete("/{uuid}", status_code=204)
async def delete_device(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="devices:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects__devices",
        _filter=Q(
            memberships__organization__projects__devices__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    return await resolver.delete_item(auth, uuid, [write_perm_subquery])
