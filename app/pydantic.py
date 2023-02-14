from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import Device, Dimension, Measure, Membership, Organization, Project, User

# Ref: https://tortoise.github.io/examples/pydantic.html#early-model-init
Tortoise.init_models(["app.models"], "models")

DeviceCreatePydantic = pydantic_model_creator(
    Device, name="DeviceCreate", exclude=("uuid", "created_at", "modified_at")
)
DeviceUpdatePydantic = pydantic_model_creator(
    Device,
    name="DeviceUpdate",
    exclude=("uuid", "created_at", "modified_at"),
    optional=("name", "type", "project_id"),
)
DeviceOutPydantic = pydantic_model_creator(Device, name="DeviceOut")

DimensionCreatePydantic = pydantic_model_creator(
    Dimension, name="DimensionCreate", exclude=("uuid", "created_at", "modified_at")
)
DimensionUpdatePydantic = pydantic_model_creator(
    Dimension,
    name="DimensionUpdate",
    exclude=("uuid", "created_at", "modified_at"),
    optional=("unit", "value", "measure_id"),
)
DimensionOutPydantic = pydantic_model_creator(Dimension, name="DimensionOut")

MeasureCreatePydantic = pydantic_model_creator(
    Measure, name="MeasureCreate", exclude=("uuid", "created_at", "modified_at")
)
MeasureUpdatePydantic = pydantic_model_creator(
    Measure,
    name="MeasureUpdate",
    exclude=("uuid", "created_at", "modified_at"),
    optional=("time", "device_id"),
)
MeasureOutPydantic = pydantic_model_creator(Measure, name="MeasureOut")

MembershipCreatePydantic = pydantic_model_creator(
    Membership, name="MembershipCreate", exclude=("uuid", "created_at", "modified_at")
)
MembershipUpdatePydantic = pydantic_model_creator(
    Membership,
    name="MembershipUpdate",
    exclude=("uuid", "created_at", "modified_at", "organization_id", "user_id"),
)
MembershipOutPydantic = pydantic_model_creator(Membership, name="MembershipOut")

OrganizationCreatePydantic = pydantic_model_creator(
    Organization,
    name="OrganizationCreate",
    exclude=("uuid", "created_at", "modified_at", "projects", "memberships"),
)
OrganizationUpdatePydantic = pydantic_model_creator(
    Organization,
    name="OrganizationUpdate",
    exclude=("uuid", "created_at", "modified_at", "projects", "memberships"),
    optional=("name", "is_active"),
)
OrganizationOutPydantic = pydantic_model_creator(Organization, name="OrganizationOut")

UserCreatePydantic = pydantic_model_creator(
    User,
    name="UserCreate",
    exclude=("uuid", "created_at", "modified_at", "memberships"),
)
UserUpdatePydantic = pydantic_model_creator(
    User,
    name="UserUpdate",
    exclude=("uuid", "created_at", "modified_at", "memberships"),
    optional=("email", "password", "is_active", "is_admin"),
)
UserOutPydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))

ProjectCreatePydantic = pydantic_model_creator(
    Project, name="ProjectCreate", exclude=("uuid", "created_at", "modified_at")
)
ProjectUpdatePydantic = pydantic_model_creator(
    Project,
    name="ProjectUpdate",
    exclude=("uuid", "created_at", "modified_at"),
    optional=(
        "name",
        "organization_id",
    ),
)
ProjectOutPydantic = pydantic_model_creator(Project, name="ProjectOut")
