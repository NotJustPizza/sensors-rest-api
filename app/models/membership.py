from tortoise import fields

from .abstract import AbstractModel


class Membership(AbstractModel):
    is_admin = fields.BooleanField(null=False, default=False)
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="memberships"
    )
    user = fields.ForeignKeyField("models.User", related_name="memberships")

    class PydanticMeta:
        exclude = ("user", "organization")
