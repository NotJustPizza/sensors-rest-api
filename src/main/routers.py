from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import HTTPNotFoundError
from .models import *

router = APIRouter()


@router.get("/")
async def index():
    return JSONResponse("Welcome!")


@router.get("/users", response_model=List[UserOutPydantic])
async def retrieve_users():
    return await UserOutPydantic.from_queryset(User.all())


@router.post("/users", response_model=UserOutPydantic, status_code=201)
async def create_user(data: UserInPydantic):
    user = await User.create(**data.dict(exclude_unset=True))
    return await UserOutPydantic.from_tortoise_orm(user)


@router.get("/users/{uuid}", response_model=UserOutPydantic)
async def retrieve_user(uuid: str):
    user = await User.get(pk=uuid)
    return await UserOutPydantic.from_tortoise_orm(user)


@router.post("/users/{uuid}", response_model=UserOutPydantic)
async def update_user(uuid: str, data: UserInPydantic):
    user = User.filter(pk=uuid).update(**data.dict(exclude_unset=True))
    return await UserOutPydantic.from_tortoise_orm(user)
