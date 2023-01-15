from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.api import create_page, resolve_params
from fastapi_pagination.ext.tortoise import paginate
from uuid import UUID
from ..dependencies import Auth
from ..exceptions import PermissionException
from ..pydantic import UserCreatePydantic, UserUpdatePydantic, UserOutPydantic
from ..models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=Page[UserOutPydantic])
async def retrieve_users(auth: Auth = Depends(Auth(scope="users:read"))):
    user = await auth.user_query
    if user.is_admin:
        return await paginate(User.all(), prefetch_related=True)
    else:
        # Workaround for paginate() not supporting passing model instance
        await user.fetch_related("memberships")
        return create_page([user], total=1, params=resolve_params())


@router.get("/{uuid}", response_model=UserOutPydantic)
async def retrieve_user(uuid: UUID, auth: Auth = Depends(Auth(scope="users:read"))):
    auth_user = await auth.user_query
    if auth_user.uuid == uuid:
        user = auth_user
    elif auth_user.is_admin:
        user = await User.get(pk=uuid)
    else:
        raise PermissionException("Missing admin permissions.")

    return await UserOutPydantic.from_tortoise_orm(user)


@router.post("/", response_model=UserOutPydantic, status_code=201)
async def create_user(
    data: UserCreatePydantic, auth: Auth = Depends(Auth(scope="users:write"))
):
    auth_user = await auth.user_query
    if not auth_user.is_admin:
        raise PermissionException("Missing admin permissions.")

    user = await User.create(**data.dict(exclude_unset=True))
    return await UserOutPydantic.from_tortoise_orm(user)


@router.post("/{uuid}", response_model=UserOutPydantic)
async def update_user(
    uuid: UUID,
    data: UserUpdatePydantic,
    auth: Auth = Depends(Auth(scope="users:write")),
):
    auth_user = await auth.user_query
    if auth_user.uuid == uuid:
        user = auth_user
    elif auth_user.is_admin:
        user = await User.get(pk=uuid)
    else:
        raise PermissionException("Missing admin permissions.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await user.save()
    return await UserOutPydantic.from_tortoise_orm(user)
