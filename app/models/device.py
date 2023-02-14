from tortoise import fields

from .abstract import AbstractModel
from .measure import Measure
from .mixins import NameMixin, TimestampMixin


class Device(NameMixin, TimestampMixin, AbstractModel):
    project = fields.ForeignKeyField(
        "models.Project", related_name="devices", null=False
    )
    type = fields.CharField(24, null=False)

    measures: fields.ReverseRelation[Measure]

    class PydanticMeta:
        exclude = ("project", "measures")
