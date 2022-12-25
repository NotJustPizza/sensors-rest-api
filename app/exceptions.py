from fastapi import HTTPException
from typing import Any
from starlette.status import HTTP_401_UNAUTHORIZED


class AuthException(HTTPException):
    def __init__(self, detail: Any = "Incorrect username or password") -> None:
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
