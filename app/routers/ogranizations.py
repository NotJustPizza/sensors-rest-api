from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from ..auth import Token
from ..dependencies import validate_token
from ..models.organization import (
    Organization,
    OrganizationInPydantic,
    OrganizationOutPydantic,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=Page[OrganizationOutPydantic])
async def retrieve_orgs(token: Token = Depends(validate_token)):
    return await paginate(Organization.all())


@router.post("/", response_model=OrganizationOutPydantic, status_code=201)
async def create_org(
    data: OrganizationInPydantic, token: Token = Depends(validate_token)
):
    user = await Organization.create(**data.dict(exclude_unset=True))
    return await OrganizationOutPydantic.from_tortoise_orm(user)


@router.get("/{uuid}", response_model=OrganizationOutPydantic)
async def retrieve_org(uuid: UUID, token: Token = Depends(validate_token)):
    user = await Organization.get(pk=uuid)
    return await OrganizationOutPydantic.from_tortoise_orm(user)


@router.post("/{uuid}", response_model=OrganizationOutPydantic)
async def update_org(
    uuid: UUID, data: OrganizationInPydantic, token: Token = Depends(validate_token)
):
    user = Organization.filter(pk=uuid).update(**data.dict(exclude_unset=True))
    return await OrganizationOutPydantic.from_tortoise_orm(user)
