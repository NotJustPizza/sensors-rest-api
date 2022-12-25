from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from .base import NameMixin, TimestampMixin, AbstractModel


class Organization(NameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    members = fields.ManyToManyField(
        "models.User", related_name="organizations", through="membership"
    )


OrganizationInPydantic = pydantic_model_creator(
    Organization, name="OrganizationIn", exclude=("uuid", "created_at", "modified_at")
)
OrganizationOutPydantic = pydantic_model_creator(Organization, name="OrganizationOut")
