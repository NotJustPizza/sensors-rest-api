from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models import Membership, Organization
from ..pydantic import (
    OrganizationCreatePydantic,
    OrganizationOutPydantic,
    OrganizationUpdatePydantic,
)
from .utils import APIResolver

router = APIRouter(prefix="/organizations", tags=["organizations"])
resolver = APIResolver(OrganizationOutPydantic, Organization)


@router.get("/", response_model=Page[OrganizationOutPydantic])
async def retrieve_organizations(
    auth: Auth = Depends(Auth(scope="organizations:read")),
):
    filter_subquery = Q(users__pk=auth.token.sub)
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=OrganizationOutPydantic)
async def retrieve_organization(
    uuid: UUID, auth: Auth = Depends(Auth(scope="organizations:read"))
):
    read_perm_subquery = Count(
        "memberships", _filter=Q(memberships__organization_id=uuid)
    )
    return await resolver.retrieve_item(auth, uuid, [read_perm_subquery])


@router.post("/", response_model=OrganizationOutPydantic, status_code=201)
async def create_organization(
    data: OrganizationCreatePydantic,
    auth: Auth = Depends(Auth(scope="organizations:write")),
):
    organization = await Organization.create(**data.dict(exclude_unset=True))
    await Membership.create(
        user_id=auth.user_uuid, organization_id=organization.uuid, is_admin=True
    )
    return await OrganizationOutPydantic.from_tortoise_orm(organization)


@router.post("/{uuid}", response_model=OrganizationOutPydantic)
async def update_organization(
    uuid: UUID,
    data: OrganizationUpdatePydantic,
    auth: Auth = Depends(Auth(scope="organizations:write")),
):
    write_perm_subquery = Count(
        "organizations",
        _filter=Q(memberships__organization_id=uuid, memberships__is_admin=True),
    )
    return await resolver.update_item(auth, uuid, data, [write_perm_subquery])


@router.delete("/{uuid}", status_code=204)
async def delete_organization(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="organizations:write")),
):
    write_perm_subquery = Count(
        "organizations",
        _filter=Q(memberships__organization_id=uuid, memberships__is_admin=True),
    )
    return await resolver.delete_item(auth, uuid, [write_perm_subquery])
