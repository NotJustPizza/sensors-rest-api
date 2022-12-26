from datetime import datetime, timedelta
from jose import jwt
from uuid import UUID
from typing import List, Union
from .settings import get_settings
from .exceptions import AuthException, PermissionException
from .models.user import User

settings = get_settings()


class Token:
    data: dict = None
    encoded_data: str = None
    __algorithm: str = "HS256"
    __user: User = None
    __secret: str = settings.app_key

    def __init__(self, data: dict, encoded_data: str):
        if "sub" not in data:
            raise AuthException("Invalid token")
        if "exp" not in data:
            raise AuthException("Invalid token")
        self.data = data
        self.encoded_data = encoded_data

    def __str__(self):
        return self.encoded_data

    @property
    def exp(self) -> int:
        return self.data["exp"]

    @property
    def sub(self) -> UUID:
        return UUID(self.data["sub"])

    @property
    def scopes(self) -> List[str]:
        if "scopes" in self.data:
            return self.data["scopes"]
        else:
            return []

    @classmethod
    def create(cls, sub: Union[str, UUID], scopes: List[str] = None):
        expire = datetime.utcnow() + timedelta(minutes=30)
        data = {"sub": str(sub), "exp": expire}
        if scopes:
            data["scopes"] = scopes
        encoded_data = jwt.encode(data, cls.__secret, algorithm=cls.__algorithm)
        return cls(data, encoded_data)

    @classmethod
    def load(cls, encoded_data: str = None):
        encoded_data = encoded_data
        data = jwt.decode(encoded_data, cls.__secret, algorithms=[cls.__algorithm])
        token = cls(data, encoded_data)
        token.verify()
        return token

    def verify(self) -> None:
        if not datetime.utcnow() < datetime.fromtimestamp(self.exp):
            raise AuthException("Expired token")

    def check_scope(self, scope: str) -> bool:
        if scope in self.scopes:
            return True
        else:
            return False

    def require_scope(self, scope: str, disable_exception: bool = False) -> None:
        if not self.check_scope(scope) and not disable_exception:
            raise PermissionException
