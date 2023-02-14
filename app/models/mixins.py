from tortoise import fields
from tortoise.validators import MinLengthValidator


class NameMixin:
    name = fields.CharField(24, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.name


class UniqueNameMixin:
    name = fields.CharField(24, unique=True, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.name


class TimestampMixin:
    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    modified_at = fields.DatetimeField(null=False, auto_now=True)
