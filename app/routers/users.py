from fastapi import APIRouter
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from tortoise.contrib.fastapi import HTTPNotFoundError
from ..models.user import User, UserInPydantic, UserOutPydantic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=Page[UserOutPydantic])
async def retrieve_users():
    return await paginate(User.all())


@router.post("/", response_model=UserOutPydantic, status_code=201)
async def create_user(data: UserInPydantic):
    user = await User.create(**data.dict(exclude_unset=True))
    return await UserOutPydantic.from_tortoise_orm(user)


@router.get("/{uuid}", response_model=UserOutPydantic)
async def retrieve_user(uuid: UUID):
    user = await User.get(pk=uuid)
    return await UserOutPydantic.from_tortoise_orm(user)


@router.post("/{uuid}", response_model=UserOutPydantic)
async def update_user(uuid: UUID, data: UserInPydantic):
    user = User.filter(pk=uuid).update(**data.dict(exclude_unset=True))
    return await UserOutPydantic.from_tortoise_orm(user)
