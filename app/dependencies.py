from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from .auth import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def validate_token(encoded_token: str = Depends(oauth2_scheme)):
    return await Token.load(encoded_token)
