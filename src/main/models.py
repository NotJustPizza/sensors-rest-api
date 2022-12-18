import re
from hashlib import sha256
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise.signals import Signals, pre_save
from tortoise.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from typing import Type, List


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


class User(TimestampMixin, NameMixin, AbstractModel):
    email = fields.CharField(
        255,
        unique=True,
        validators=[
            RegexValidator(
                r"^[a-z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*$",
                flags=re.ASCII,
            )
        ],
    )
    password = fields.CharField(64, null=True)


@pre_save(User)
async def user_pre_save(
    sender: "Type[User]",
    instance: User,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    if not update_fields or "password" in update_fields:
        instance.password = sha256(str(instance.password).encode("utf-8")).hexdigest()


UserInPydantic = pydantic_model_creator(
    User, name="UserIn", exclude=("uuid", "created_at", "modified_at")
)
UserOutPydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
