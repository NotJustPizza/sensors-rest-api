from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from .models import db_models
from .models.user import User
from .models.organization import Organization, OrganizationMemberships

Tortoise.init_models(db_models, "models")

UserInPydantic = pydantic_model_creator(
    User, name="UserIn", exclude=("uuid", "created_at", "modified_at", "memberships")
)
UserOutPydantic = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password",),
)

OrganizationInPydantic = pydantic_model_creator(
    Organization,
    name="OrganizationIn",
    exclude=("uuid", "created_at", "modified_at", "memberships"),
)
OrganizationOutPydantic = pydantic_model_creator(Organization, name="OrganizationOut")
