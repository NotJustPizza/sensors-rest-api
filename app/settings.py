from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_key: str
    admin_pass: str
    db_provider: str = "asyncpg"
    db_host: str = "database"
    db_port: int = "5432"
    db_user: str = "postgres"
    db_pass: str = None
    db_name: str = "sensors"
    custom_db_url: str = None

    @property
    def db_url(self):
        if self.custom_db_url:
            return self.custom_db_url
        else:
            return f"{self.db_provider}://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache()
def get_settings():
    return Settings()
