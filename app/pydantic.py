from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from .models import db_models
from .models.user import User
from .models.organization import Organization
from .models.project import Project

# Ref: https://tortoise.github.io/examples/pydantic.html#early-model-init
Tortoise.init_models(db_models, "models")

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


ProjectCreatePydantic = pydantic_model_creator(
    Project, name="ProjecCreate", exclude=("uuid", "created_at", "modified_at")
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
