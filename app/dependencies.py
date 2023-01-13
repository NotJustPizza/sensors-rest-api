from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from uuid import UUID
from tortoise.queryset import QuerySetSingle
from .settings import Settings
from .auth import Token
from .exceptions import AuthException
from .models.user import User


@lru_cache()
def get_settings():
    return Settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class Auth:
    scope: str
    token: Token

    def __init__(self, scope: str = None):
        self.scope = scope

    def __call__(
        self,
        settings: Settings = Depends(get_settings),
        encoded_token: str = Depends(oauth2_scheme),
    ):
        self.token = Token.load(settings.app_key, encoded_token)
        if not self.scope:
            return self
        if self.scope not in self.token.scopes and "global" not in self.token.scopes:
            raise AuthException(f"Missing required scope: {self.scope}")
        return self

    @property
    def user_query(self) -> QuerySetSingle[User]:
        return User.get(pk=self.token.sub)

    @property
    def user_uuid(self) -> UUID:
        return self.token.sub
