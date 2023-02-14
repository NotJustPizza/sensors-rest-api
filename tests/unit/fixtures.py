from typing import List

from pytest import fixture

from app.models import (
    Device,
    Dimension,
    Measure,
    Membership,
    Organization,
    Project,
    User,
)

from .utils import populate_objects


@fixture(scope="function", name="users", autouse=True)
async def populate_users(auth_user: User) -> List[User]:
    users = [auth_user]
    users += await populate_objects(
        [
            {"email": "john@example.com"},
            {"email": "chad@example.com"},
            {"email": "sarah@example.com"},
            {"email": "mike@example.com"},
            {"email": "dane@example.com"},
        ],
        User,
    )
    return users


@fixture(scope="function", name="organizations", autouse=True)
async def populate_organizations() -> List[Organization]:
    return await populate_objects(
        [{"name": "Space"}, {"name": "Miners"}, {"name": "Pilots"}, {"name": "Cars"}],
        Organization,
    )


@fixture(scope="function", name="memberships", autouse=True)
async def populate_memberships(
    organizations: List[Organization], users: List[User]
) -> List[Membership]:
    # We need at least 6 users to have enough to assign
    assert len(users) >= 6
    memberships = []

    # We assign every user to 2 organizations
    for index, user in enumerate(users):
        # user[0] -> organization[0:2]
        # user[1] -> organization[0:2]
        # user[2] -> organization[1:3]
        # ...
        for organization in organizations[index // 2 : index // 2 + 2]:
            membership = await Membership.create(
                user_id=user.uuid,
                organization_id=organization.uuid,
                is_admin=index == 0,
            )
            memberships.append(membership)
    return memberships


@fixture(scope="function", name="projects", autouse=True)
async def populate_projects(organizations: List[Organization]) -> List[Project]:
    # We need at least 4 organizations to have enough to assign
    assert len(organizations) >= 4

    data = [
        {"name": "Rocket"},
        {"name": "Asteroid"},
        {"name": "Excavation"},
        {"name": "Mine"},
        {"name": "Reconnaissance"},
        {"name": "Cargo"},
        {"name": "Transport"},
        {"name": "Travel"},
    ]

    # We assign 2 projects per organization
    for index, item in enumerate(data):
        # project[0] -> organization[0]
        # project[1] -> organization[0]
        # project[2] -> organization[1]
        # ...
        item["organization_id"] = organizations[index // 2].uuid
    return await populate_objects(data, Project)


@fixture(scope="function", name="devices", autouse=True)
async def populate_devices(projects: List[Project]) -> List[Device]:
    source_data = [
        {"name": "Camera", "type": "Arduino"},
        {"name": "Sensor", "type": "Arduino"},
        {"name": "Device", "type": "Raspberry"},
    ]
    data = []

    # We assign three devices per project
    for project in projects:
        for source_item in source_data:
            item = source_item.copy()
            item["project_id"] = project.uuid
            data.append(item)
    return await populate_objects(data, Device)


@fixture(scope="function", name="measures", autouse=True)
async def populate_measures(devices: List[Device]) -> List[Measure]:
    source_data = [
        {"measured_at": "2021-11-02 10:04:00"},
        {"measured_at": "2021-11-02 10:05:00"},
        {"measured_at": "2021-11-03 18:00:00+02:00"},
    ]
    data = []

    # We assign three measures per device
    for device in devices:
        for source_item in source_data:
            item = source_item.copy()
            item["device_id"] = device.uuid
            data.append(item)
    return await populate_objects(data, Measure)


@fixture(scope="function", name="dimensions", autouse=True)
async def populate_dimensions(measures: List[Measure]) -> List[Dimension]:
    source_data = [
        {"value": "3.123", "unit": "seconds"},
        {"value": "54.12", "unit": "kelvin"},
    ]
    data = []

    # We assign two dimensions per measure
    for measure in measures:
        for source_item in source_data:
            item = source_item.copy()
            item["measure_id"] = measure.uuid
            data.append(item)
    return await populate_objects(data, Dimension)
