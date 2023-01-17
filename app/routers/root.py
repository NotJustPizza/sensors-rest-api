from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, ValidationError

from ..auth import Token
from ..dependencies import Auth, get_settings
from ..exceptions import AuthException
from ..settings import Settings
from .users import User

router = APIRouter(tags=["root"])


@router.get("/")
async def index(auth: Auth = Depends(Auth())):
    user = await auth.user_query.only("email")
    return f"Welcome {user.email}!"


class TokenPydantic(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenPydantic)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
):
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

    token = Token.create(settings.app_key, user.uuid, scopes=form_data.scopes)

    return {"access_token": str(token), "token_type": "bearer"}
