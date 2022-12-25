from argon2 import PasswordHasher
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist
from ..auth import Token
from ..exceptions import AuthException
from ..dependencies import validate_token
from .users import User


router = APIRouter(tags=["root"])


@router.get("/")
async def index(token: Token = Depends(validate_token)):
    user = await token.get_user()
    return f"Welcome {user.email}!"


class TokenPydantic(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenPydantic)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await User.get(email=form_data.username)
    except DoesNotExist:
        raise AuthException()

    hasher = PasswordHasher()

    if not hasher.verify(user.password, form_data.password):
        raise AuthException()

    if hasher.check_needs_rehash(user.password):
        user.password = form_data.password
        await user.save()

    token = await Token.create(sub=str(user.uuid))

    return {"access_token": str(token), "token_type": "bearer"}
