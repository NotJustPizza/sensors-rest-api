import re
from tortoise import fields
from tortoise.models import Model
from tortoise.validators import RegexValidator


class AbstractModel(Model):
    uuid = fields.UUIDField(pk=True)

    class Meta:
        abstract = True


class NameMixin:
    name = fields.CharField(
        32, unique=True, validators=[RegexValidator(r"^[a-z]{3,24}$", flags=re.ASCII)]
    )

    def __str__(self):
        return self.name


class TimestampMixin:
    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    modified_at = fields.DatetimeField(null=False, auto_now=True)
