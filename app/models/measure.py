from tortoise import fields

from .abstract import AbstractModel
from .dimension import Dimension
from .mixins import TimestampMixin


class Measure(TimestampMixin, AbstractModel):
    measured_at = fields.DatetimeField(null=False)
    device = fields.ForeignKeyRelation(
        "models.Device", related_name="measures", null=False
    )

    dimensions: fields.ReverseRelation[Dimension]

    class PydanticMeta:
        exclude = ("device", "dimensions")
