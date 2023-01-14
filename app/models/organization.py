from tortoise import fields
from .base import NameMixin, TimestampMixin, AbstractModel


class OrganizationMemberships(AbstractModel):
    is_admin = fields.BooleanField(null=False, default=False)
    user = fields.ForeignKeyField("models.User", related_name="memberships")
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="memberships"
    )

    class Meta:
        table = "organization_memberships"

    class PydanticMeta:
        exclude = ("user", "organization")


class Organization(NameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    users = fields.ManyToManyField(
        "models.User", related_name="organizations", through="organization_memberships"
    )
    memberships: fields.ReverseRelation[OrganizationMemberships]

    class PydanticMeta:
        exclude = ("users",)


__models__ = [Organization, OrganizationMemberships]
