from tortoise import fields

from .abstract import AbstractModel
from .device import Device
from .mixins import NameMixin, TimestampMixin


class Project(NameMixin, TimestampMixin, AbstractModel):
    is_active = fields.BooleanField(null=False, default=True)
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="projects", null=False
    )

    devices: fields.ReverseRelation[Device]

    class PydanticMeta:
        exclude = ("organization", "devices")
