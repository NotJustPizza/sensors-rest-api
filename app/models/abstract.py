from tortoise import fields
from tortoise.models import Model


class AbstractModel(Model):
    uuid = fields.UUIDField(pk=True)

    class Meta:
        abstract = True
