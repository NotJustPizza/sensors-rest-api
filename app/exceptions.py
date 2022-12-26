from fastapi import HTTPException
from typing import Any
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


class AuthException(HTTPException):
    def __init__(self, detail: Any = "Incorrect username or password") -> None:
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionException(HTTPException):
    def __init__(self, detail: Any = "Missing required permission") -> None:
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
