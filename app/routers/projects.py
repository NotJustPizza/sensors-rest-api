from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from tortoise.expressions import Q
from tortoise.functions import Count
from ..dependencies import Auth
from ..exceptions import PermissionException
from ..models.project import Project
from ..pydantic import ProjectCreatePydantic, ProjectUpdatePydantic, ProjectOutPydantic

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=Page[ProjectOutPydantic])
async def retrieve_projects(
    auth: Auth = Depends(Auth(scope="projects:read")),
):
    user = await auth.user_query.only("is_admin")
    if user.is_admin:
        query = Project.all()
    else:
        query = Project.filter(organization__users__pk=auth.token.sub)
    return await paginate(query)


@router.get("/{uuid}", response_model=ProjectOutPydantic)
async def retrieve_project(
    uuid: UUID, auth: Auth = Depends(Auth(scope="projects:read"))
):
    user = await auth.user_query.only("is_admin").annotate(
        has_organization=Count(
            "memberships__organization__projects",
            _filter=Q(memberships__organization__projects__pk=uuid),
        )
    )
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.has_organization:
        raise PermissionException("Missing organization permissions.")

    project = await Project.get(pk=uuid)
    return await ProjectOutPydantic.from_tortoise_orm(project)


@router.post("/", response_model=ProjectOutPydantic, status_code=201)
async def create_project(
    data: ProjectCreatePydantic,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    user = await auth.user_query.only("is_admin").annotate(
        is_organization_admin=Count(
            "memberships",
            _filter=Q(
                memberships__organization_id=data.organization_id,
                memberships__is_admin=True,
            ),
        )
    )
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.is_organization_admin:
        raise PermissionException("Missing organization admin permissions.")

    project = await Project.create(**data.dict(exclude_unset=True))
    return await ProjectOutPydantic.from_tortoise_orm(project)


@router.post("/{uuid}", response_model=ProjectOutPydantic)
async def update_project(
    uuid: UUID,
    data: ProjectUpdatePydantic,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    data = data.dict(exclude_unset=True)
    user_query = auth.user_query.only("is_admin").annotate(
        is_current_organization_admin=Count(
            "memberships__organization__projects",
            _filter=Q(
                memberships__organization__projects__pk=uuid,
                memberships__is_admin=True,
            ),
        )
    )

    if "organization_id" in data:
        user_query = user_query.annotate(
            is_new_organization_admin=Count(
                "memberships__organization__projects",
                _filter=Q(
                    memberships__organization__pk=data["organization_id"],
                    memberships__is_admin=True,
                ),
            )
        )
    user = await user_query
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.is_current_organization_admin:
        raise PermissionException(
            "Missing permissions to project's current organization."
        )

    project = await Project.get(pk=uuid)
    for key, value in data.items():
        if key == "organization_id":
            # noinspection PyUnresolvedReferences
            if not user.is_admin and not user.is_new_organization_admin:
                raise PermissionException(
                    "Missing permissions to project's new organization."
                )
        setattr(project, key, value)

    await project.save()
    return await ProjectOutPydantic.from_tortoise_orm(project)


@router.delete("/{uuid}", status_code=204)
async def delete_project(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="projects:write")),
):
    user = await auth.user_query.only("is_admin").annotate(
        is_organization_admin=Count(
            "memberships__organization__projects",
            _filter=Q(
                memberships__organization__projects__pk=uuid,
                memberships__is_admin=True,
            ),
        )
    )
    # noinspection PyUnresolvedReferences
    if not user.is_admin and not user.is_organization_admin:
        raise PermissionException("Missing permissions to project's organization.")

    project = await Project.get(pk=uuid)
    await project.delete()
