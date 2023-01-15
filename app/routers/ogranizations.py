from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from tortoise.expressions import Q
from tortoise.functions import Count
from ..dependencies import Auth
from ..exceptions import PermissionException
from ..models.organization import Organization, OrganizationMemberships
from ..pydantic import (
    OrganizationCreatePydantic,
    OrganizationUpdatePydantic,
    OrganizationOutPydantic,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=Page[OrganizationOutPydantic])
async def retrieve_organizations(
    auth: Auth = Depends(Auth(scope="organizations:read")),
):
    user = await auth.user_query.only("is_admin")
    if user.is_admin:
        query = Organization.all()
    else:
        query = Organization.filter(users__pk=auth.token.sub)
    return await paginate(query, prefetch_related=True)


@router.get("/{uuid}", response_model=OrganizationOutPydantic)
async def retrieve_organization(
    uuid: UUID, auth: Auth = Depends(Auth(scope="organizations:read"))
):
    user = await auth.user_query.only("is_admin").annotate(
        has_organization=Count(
            "memberships", _filter=Q(memberships__organization_id=uuid)
        )
    )
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.has_organization:
        raise PermissionException("Missing organization permissions.")

    organization = await Organization.get(pk=uuid)
    return await OrganizationOutPydantic.from_tortoise_orm(organization)


@router.post("/", response_model=OrganizationOutPydantic, status_code=201)
async def create_organization(
    data: OrganizationCreatePydantic,
    auth: Auth = Depends(Auth(scope="organizations:write")),
):
    organization = await Organization.create(**data.dict(exclude_unset=True))
    await OrganizationMemberships.create(
        user_id=auth.user_uuid, organization_id=organization.uuid, is_admin=True
    )
    return await OrganizationOutPydantic.from_tortoise_orm(organization)


@router.post("/{uuid}", response_model=OrganizationOutPydantic)
async def update_organization(
    uuid: UUID,
    data: OrganizationUpdatePydantic,
    auth: Auth = Depends(Auth(scope="organizations:write")),
):
    user = await auth.user_query.only("is_admin").annotate(
        is_organization_admin=Count(
            "organizations",
            _filter=Q(memberships__organization_id=uuid, memberships__is_admin=True),
        )
    )
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.is_organization_admin:
        raise PermissionException("Missing organization admin permissions.")

    organization = await Organization.get(pk=uuid)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(organization, key, value)

    await organization.save()
    return await OrganizationOutPydantic.from_tortoise_orm(organization)
