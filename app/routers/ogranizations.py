from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from tortoise.exceptions import DoesNotExist
from ..auth import Token
from ..dependencies import validate_token
from ..exceptions import PermissionException
from ..models.organization import (
    Organization,
    OrganizationInPydantic,
    OrganizationOutPydantic,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=Page[OrganizationOutPydantic])
async def retrieve_orgs(token: Token = Depends(validate_token)):
    if token.check_scope("admin"):
        query = Organization.all()
    else:
        query = Organization.filter(members__pk=token.sub)
    return await paginate(query)


@router.post("/", response_model=OrganizationOutPydantic, status_code=201)
async def create_org(
    data: OrganizationInPydantic, token: Token = Depends(validate_token)
):
    token.require_scope("admin")
    user = await Organization.create(**data.dict(exclude_unset=True))
    return await OrganizationOutPydantic.from_tortoise_orm(user)


@router.get("/{uuid}", response_model=OrganizationOutPydantic)
async def retrieve_org(uuid: UUID, token: Token = Depends(validate_token)):
    if token.check_scope("admin"):
        org = await Organization.get(pk=uuid)
    else:
        try:
            org = await Organization.get(pk=uuid, members__pk=token.sub)
        except DoesNotExist:
            raise PermissionException

    return await OrganizationOutPydantic.from_tortoise_orm(org)


@router.post("/{uuid}", response_model=OrganizationOutPydantic)
async def update_org(
    uuid: UUID, data: OrganizationInPydantic, token: Token = Depends(validate_token)
):
    token.require_scope("admin")
    user = Organization.filter(pk=uuid).update(**data.dict(exclude_unset=True))
    return await OrganizationOutPydantic.from_tortoise_orm(user)
