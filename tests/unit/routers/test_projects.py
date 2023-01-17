from typing import List

from pytest import mark

from app.models.organization import Organization
from app.models.project import Project

from ..asserts import assert_object_matches_json, assert_object_was_deleted
from ..utils import ApiTestClient

pytestmark = mark.anyio
pytest_plugins = "tests.unit.routers.fixtures"


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "projects:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, expected_total",
    [[{"admin": True}, 8], [{"admin": False}, 4]],
    indirect=["auth_context"],
)
async def test_retrieve_projects(
    auth_client: ApiTestClient, projects: List[Project], expected_total: int
):
    items = auth_client.api_list("/projects", expected_total)
    for i in range(expected_total):
        await assert_object_matches_json(projects[i], items[i])


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "projects:read"}],
    indirect=True,
)
async def test_retrieve_project(auth_client: ApiTestClient, projects: List[Project]):
    project = projects[0]
    item = auth_client.api_get("/projects", project.uuid)
    await assert_object_matches_json(project, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "projects:write"}],
    indirect=True,
)
async def test_create_project(
    auth_client: ApiTestClient, organizations: List[Organization]
):
    data = {"name": "moon", "organization_id": str(organizations[0].uuid)}
    item = auth_client.api_create("/projects", data)
    project = await Project.get(**data)
    await assert_object_matches_json(project, item)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "projects:write"}],
    indirect=True,
)
async def test_update_project(
    auth_client: ApiTestClient,
    projects: List[Project],
    organizations: List[Organization],
):
    project = projects[0]
    data = {"name": "moon", "organization_id": str(organizations[1].uuid)}
    item = auth_client.api_update("/projects", project.uuid, data)
    await assert_object_matches_json(project, item, refresh=True)
    await assert_object_matches_json(project, data)


@mark.parametrize(
    "auth_client",
    [{"scope": "global"}, {"scope": "projects:write"}],
    indirect=True,
)
async def test_delete_project(auth_client: ApiTestClient, projects: List[Project]):
    project = projects[0]
    auth_client.api_delete("/projects", project.uuid)
    await assert_object_was_deleted(project)
