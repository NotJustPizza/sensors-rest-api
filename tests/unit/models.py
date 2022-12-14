from src.main.models import AbstractModel, NameMixin, TimestampMixin


class BaseTestModel(TimestampMixin, NameMixin, AbstractModel):
    pass
