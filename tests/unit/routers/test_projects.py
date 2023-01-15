from fastapi.testclient import TestClient
from pytest import mark, raises
from tortoise.exceptions import DoesNotExist
from typing import List
from app.models.organization import Organization
from app.models.project import Project
from ..asserts import assert_pagination, assert_object

pytestmark = mark.anyio
pytest_plugins = "tests.unit.routers.fixtures"


def assert_project_object(project_json: dict, org: Project):
    assert_object(project_json, org)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "projects:read"}],
    indirect=True,
)
@mark.parametrize(
    "auth_context, total",
    [[{"admin": True}, 8], [{"admin": False}, 4]],
    indirect=["auth_context"],
)
async def test_retrieve_projects(
    logged_client: TestClient, projects: List[Project], total: int
):
    response = logged_client.get("/projects")
    assert response.status_code == 200

    json = response.json()
    assert_pagination(json, total=total)

    for i in range(total):
        assert_project_object(json["items"][i], projects[i])


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "projects:read"}],
    indirect=True,
)
async def test_retrieve_project(logged_client: TestClient, projects: List[Project]):
    project = projects[0]
    response = logged_client.get(f"/projects/{project.uuid}")
    assert response.status_code == 200

    project_json = response.json()
    assert_project_object(project_json, project)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "projects:write"}],
    indirect=True,
)
async def test_create_project(
    logged_client: TestClient, organizations: List[Organization]
):
    data = {"name": "moon", "organization_id": str(organizations[0].uuid)}

    response = logged_client.post("/projects", json=data)
    assert response.status_code == 201

    project_json = response.json()
    project = await Project.get(**data)

    assert_project_object(project_json, project)


@mark.parametrize(
    "logged_client",
    [{"scope": "global"}, {"scope": "projects:write"}],
    indirect=True,
)
async def test_update_project(
    logged_client: TestClient,
    projects: List[Project],
    organizations: List[Organization],
):
    project = projects[0]
    project_data = {"name": "moon", "organization_id": str(organizations[1].uuid)}

    response = logged_client.post(f"/projects/{project.uuid}", json=project_data)
    assert response.status_code == 200

    await project.refresh_from_db()
    assert project.name == project_data["name"]
    assert str(project.organization_id) == project_data["organization_id"]

    assert_project_object(response.json(), project)


@mark.parametrize(
    "logged_client", [{"scope": "global"}, {"scope": "projects:write"}], indirect=True
)
async def test_delete_project(logged_client: TestClient, projects: List[Project]):
    project = projects[0]

    response = logged_client.delete(f"/projects/{project.uuid}")
    assert response.status_code == 204

    with raises(DoesNotExist):
        await project.refresh_from_db()
