from tortoise import fields

from .abstract import AbstractModel
from .membership import Membership
from .mixins import TimestampMixin, UniqueNameMixin
from .project import Project


class Organization(UniqueNameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    users = fields.ManyToManyField(
        "models.User", related_name="organizations", through="membership"
    )

    memberships: fields.ReverseRelation[Membership]
    projects: fields.ReverseRelation[Project]

    class PydanticMeta:
        exclude = ("users",)
