from app.models.base import AbstractModel, NameMixin, TimestampMixin


class BaseTestModel(TimestampMixin, NameMixin, AbstractModel):
    pass
