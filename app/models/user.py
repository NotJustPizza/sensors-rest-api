import re
from argon2 import PasswordHasher
from tortoise import fields, BaseDBAsyncClient
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.signals import pre_save
from tortoise.validators import RegexValidator
from typing import Type, List, Optional
from .base import TimestampMixin, AbstractModel
from .organization import Organization, OrganizationMembership


class User(TimestampMixin, AbstractModel):
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
    password = fields.CharField(97, null=True)
    organizations: fields.ReverseRelation[Organization]
    membership: fields.ReverseRelation[OrganizationMembership]
    is_active = fields.BooleanField(null=False, default=True)
    is_admin = fields.BooleanField(null=False, default=False)

    class PydanticMeta:
        exclude = ("membership", "organizations")


@pre_save(User)
async def user_pre_save(
    sender: Type[User],
    instance: User,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: List[str],
) -> None:
    if (not update_fields or "password" in update_fields) and instance.password:
        hasher = PasswordHasher()
        instance.password = hasher.hash(instance.password)


UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude=("uuid", "created_at", "modified_at"),
)
UserOutPydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
