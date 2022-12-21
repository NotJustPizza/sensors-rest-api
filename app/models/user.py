import re
from hashlib import sha256
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.signals import pre_save
from tortoise.validators import RegexValidator
from typing import Type, List
from .base import TimestampMixin, NameMixin, AbstractModel


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
