from tortoise import fields

from .base import AbstractModel, NameMixin, TimestampMixin


class Project(NameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="projects", null=False
    )

    class PydanticMeta:
        exclude = ("organization",)


__models__ = [Project]
