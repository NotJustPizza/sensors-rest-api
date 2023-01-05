from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, ValidationError
from ..auth import Token
from ..exceptions import AuthException
from ..dependencies import validate_token
from .users import User


router = APIRouter(tags=["root"])


@router.get("/")
async def index(token: Token = Depends(validate_token)):
    user = await User.get(pk=token.sub)
    return f"Welcome {user.email}!"


class TokenPydantic(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenPydantic)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await User.get(email=form_data.username)
    except (DoesNotExist, ValidationError):
        raise AuthException()

    if not user.is_active or not user.password:
        raise AuthException("User disabled")

    hasher = PasswordHasher()

    try:
        hasher.verify(user.password, form_data.password)
    except VerifyMismatchError:
        raise AuthException()

    if hasher.check_needs_rehash(user.password):
        user.password = form_data.password
        await user.save()

    scopes = "admin" if user.is_admin else None
    token = Token.create(sub=user.uuid, scopes=scopes)

    return {"access_token": str(token), "token_type": "bearer"}
