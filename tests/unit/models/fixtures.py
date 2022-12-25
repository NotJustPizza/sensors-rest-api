from app.models.base import AbstractModel, NameMixin, TimestampMixin


class BaseTestModel(NameMixin, TimestampMixin, AbstractModel):
    pass
