from typing import List, Optional, Type

from argon2 import PasswordHasher
from tortoise import BaseDBAsyncClient, fields
from tortoise.signals import pre_save

from ..validators import EmailValidator
from .base import AbstractModel, TimestampMixin
from .organization import Organization, OrganizationMemberships


class User(TimestampMixin, AbstractModel):
    email = fields.CharField(
        255,
        unique=True,
        validators=[EmailValidator()],
    )
    password = fields.CharField(97, null=True)
    is_active = fields.BooleanField(null=False, default=True)
    is_admin = fields.BooleanField(null=False, default=False)
    organizations: fields.ReverseRelation[Organization]
    memberships: fields.ReverseRelation[OrganizationMemberships]

    class PydanticMeta:
        exclude = ("organizations",)


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


__models__ = [User]
