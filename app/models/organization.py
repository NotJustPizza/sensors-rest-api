from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from .base import NameMixin, TimestampMixin, AbstractModel


class Organization(NameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    users = fields.ManyToManyField(
        "models.User", related_name="organizations", through="organization_membership"
    )


class OrganizationMembership(Model):
    is_admin = fields.BooleanField(null=False, default=False)
    user = fields.ForeignKeyField("models.User", related_name="membership")
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="membership"
    )

    class Meta:
        table = "organization_membership"


OrganizationInPydantic = pydantic_model_creator(
    Organization, name="OrganizationIn", exclude=("uuid", "created_at", "modified_at")
)
OrganizationOutPydantic = pydantic_model_creator(Organization, name="OrganizationOut")
