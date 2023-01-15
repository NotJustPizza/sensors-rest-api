from pytest import fixture
from typing import List
from app.models.user import User
from app.models.organization import Organization, OrganizationMemberships
from app.models.project import Project
from ..utils import AuthContext, populate_objects


@fixture(scope="function", name="users")
async def populate_users(auth_context: AuthContext):
    # Auth user was already populated, so has to be added there
    users = [auth_context.user]
    users += await populate_objects(
        [
            {"email": "john@example.com"},
            {"email": "chad@example.com"},
            {"email": "sarah@example.com"},
            {"email": "mike@example.com"},
            {"email": "dane@example.com"},
            {"email": "anna@example.com"},
            {"email": "daniel@example.com"},
        ],
        User,
    )

    return users


@fixture(scope="function", name="organizations")
async def populate_organizations(auth_context: AuthContext, users: List[User]):
    # We need at least 8 users to have enough to assign
    assert len(users) >= 8

    organizations = await populate_objects(
        [
            {"name": "space"},
            {"name": "miners"},
            {"name": "pilots"},
            {"name": "nomads"},
        ],
        Organization,
    )

    # We assign every user to 2 organizations
    for index, user in enumerate(users):
        # user[0] -> organization[0:2]
        # user[1] -> organization[0:2]
        # user[2] -> organization[1:3]
        # ...
        for organization in organizations[index // 2 : index // 2 + 2]:
            await OrganizationMemberships.create(
                user_id=user.uuid,
                organization_id=organization.uuid,
                # Only auth user should be admin
                is_admin=index == 0,
            )
    return organizations


@fixture(scope="function", name="projects")
async def populate_projects(
    auth_context: AuthContext, organizations: List[Organization]
):
    # We need at least 4 organizations to have enough to assign
    assert len(organizations) >= 4

    data = [
        {"name": "rocket"},
        {"name": "asteroid"},
        {"name": "excavation"},
        {"name": "mine"},
        {"name": "reconnaissance"},
        {"name": "cargo"},
        {"name": "travel"},
        {"name": "fishing"},
    ]

    # We assign two projects per organizations
    for index, item in enumerate(data):
        # project[0] -> organization[0]
        # project[1] -> organization[0]
        # project[2] -> organization[1]
        # ...
        item["organization_id"] = organizations[index // 2].uuid
    return await populate_objects(data, Project)
