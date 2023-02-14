from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models.project import Project
from ..pydantic import ProjectCreatePydantic, ProjectOutPydantic, ProjectUpdatePydantic
from .utils import APIResolver

router = APIRouter(prefix="/projects", tags=["projects"])
resolver = APIResolver(ProjectOutPydantic, Project)


@router.get("/", response_model=Page[ProjectOutPydantic])
async def retrieve_projects(
    auth: Auth = Depends(Auth(scope="projects:read")),
):
    filter_subquery = Q(organization__users__pk=auth.token.sub)
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=ProjectOutPydantic)
async def retrieve_project(
    uuid: UUID, auth: Auth = Depends(Auth(scope="projects:read"))
):
    read_perm_subquery = Count(
        "memberships__organization__projects",
        _filter=Q(memberships__organization__projects__pk=uuid),
    )
    return await resolver.retrieve_item(auth, uuid, [read_perm_subquery])


@router.post("/", response_model=ProjectOutPydantic, status_code=201)
async def create_project(
    data: ProjectCreatePydantic,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    write_perm_subquery = Count(
        "memberships",
        _filter=Q(
            memberships__organization_id=data.organization_id,
            memberships__is_admin=True,
        ),
    )
    return await resolver.create_item(auth, data, [write_perm_subquery])


@router.post("/{uuid}", response_model=ProjectOutPydantic)
async def update_project(
    uuid: UUID,
    data: ProjectUpdatePydantic,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects",
        _filter=Q(
            memberships__organization__projects__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    field_write_perm_subqueries = {
        "organization_id": Count(
            "memberships__organization__projects",
            _filter=Q(
                memberships__organization__pk=data.organization_id,
                memberships__is_admin=True,
            ),
        )
    }

    return await resolver.update_item(
        auth, uuid, data, [write_perm_subquery], field_write_perm_subqueries
    )


@router.delete("/{uuid}", status_code=204)
async def delete_project(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    write_perm_subquery = Count(
        "memberships__organization__projects",
        _filter=Q(
            memberships__organization__projects__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    return await resolver.delete_item(auth, uuid, [write_perm_subquery])
