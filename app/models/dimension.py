from tortoise import fields

from .abstract import AbstractModel
from .mixins import TimestampMixin


class Dimension(TimestampMixin, AbstractModel):
    measure = fields.ForeignKeyField(
        "models.Measure", related_name="dimensions", null=False
    )
    # TODO: Create validation for named units and any other Si derived
    unit = fields.CharField(24)
    value = fields.FloatField()

    class PydanticMeta:
        exclude = ("measure",)
