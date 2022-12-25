from datetime import datetime, timedelta
from jose import jwt
from .settings import get_settings
from .exceptions import AuthException
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
    def exp(self):
        return self.data["exp"]

    @property
    def sub(self):
        return self.data["sub"]

    async def get_user(self) -> User:
        if not self.__user:
            self.__user = await User.get(pk=self.sub)
        return self.__user

    @classmethod
    async def create(cls, sub: str):
        expire = datetime.utcnow() + timedelta(minutes=30)
        data = {"sub": sub, "exp": expire}
        encoded_data = jwt.encode(data, cls.__secret, algorithm=cls.__algorithm)
        return cls(data, encoded_data)

    @classmethod
    async def load(cls, encoded_data: str = None):
        encoded_data = encoded_data
        data = jwt.decode(encoded_data, cls.__secret, algorithms=[cls.__algorithm])
        token = cls(data, encoded_data)
        await token.verify()
        return token

    async def verify(self) -> None:
        if not datetime.utcnow() < datetime.fromtimestamp(self.exp):
            raise AuthException("Expired token")
        user = await self.get_user()
        if not user.is_active:
            raise AuthException("User disabled")
