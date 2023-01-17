from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from jose import jwt

from .exceptions import AuthException


class Token:
    data: dict
    encoded_data: str
    __algorithm: str = "HS256"

    def __init__(self, data: dict, encoded_data: str):
        if "sub" not in data or "exp" not in data:
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
    def create(cls, secret: str, sub: str | UUID, scopes: List[str] | None = None):
        expire = datetime.utcnow() + timedelta(minutes=30)
        data = {"sub": str(sub), "exp": expire}
        if scopes:
            data["scopes"] = scopes
        encoded_data = jwt.encode(data, secret, algorithm=cls.__algorithm)
        return cls(data, encoded_data)

    @classmethod
    def load(cls, secret: str, encoded_data: str):
        encoded_data = encoded_data
        data = jwt.decode(encoded_data, secret, algorithms=[cls.__algorithm])
        token = cls(data, encoded_data)
        token.verify()
        return token

    def verify(self) -> None:
        if not datetime.utcnow() < datetime.fromtimestamp(self.exp):
            raise AuthException("Expired token")
