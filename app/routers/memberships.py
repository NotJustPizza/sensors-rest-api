from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from tortoise.expressions import Q
from tortoise.functions import Count

from ..dependencies import Auth
from ..models.membership import Membership
from ..pydantic import (
    MembershipCreatePydantic,
    MembershipOutPydantic,
    MembershipUpdatePydantic,
)
from .utils import APIResolver

router = APIRouter(prefix="/memberships", tags=["memberships"])
resolver = APIResolver(MembershipOutPydantic, Membership)


@router.get("/", response_model=Page[MembershipOutPydantic])
async def retrieve_memberships(auth: Auth = Depends(Auth(scope="memberships:read"))):
    filter_subquery = Q(
        Q(user_id=auth.token.sub),
        Q(organization__users__pk=auth.token.sub),
        join_type="OR",
    )
    return await resolver.retrieve_page(auth, filter_subquery)


@router.get("/{uuid}", response_model=MembershipOutPydantic)
async def retrieve_membership(
    uuid: UUID, auth: Auth = Depends(Auth(scope="memberships:read"))
):
    read_perm_subqueries = [
        Count("memberships", _filter=Q(memberships__pk=uuid)),
        Count(
            "memberships",
            _filter=Q(
                memberships__organization__memberships__pk=uuid,
                memberships__is_admin=True,
            ),
        ),
    ]
    return await resolver.retrieve_item(auth, uuid, read_perm_subqueries)


@router.post("/", response_model=MembershipOutPydantic, status_code=201)
async def create_membership(
    data: MembershipCreatePydantic,
    auth: Auth = Depends(Auth(scope="memberships:write")),
):
    write_perm_subquery = Count(
        "memberships",
        _filter=Q(
            memberships__organization_id=data.organization_id,
            memberships__is_admin=True,
        ),
    )
    return await resolver.create_item(auth, data, [write_perm_subquery])


@router.post("/{uuid}", response_model=MembershipOutPydantic)
async def update_membership(
    uuid: UUID,
    data: MembershipUpdatePydantic,
    auth: Auth = Depends(Auth(scope="memberships:write")),
):
    write_perm_subquery = Count(
        "memberships",
        _filter=Q(
            memberships__organization__memberships__pk=uuid,
            memberships__is_admin=True,
        ),
    )
    return await resolver.update_item(auth, uuid, data, [write_perm_subquery])


@router.delete("/{uuid}", status_code=204)
async def delete_membership(
    uuid: UUID,
    auth: Auth = Depends(Auth(scope="memberships:write")),
):
    write_perm_subqueries = [
        Count("memberships", _filter=Q(memberships__pk=uuid)),
        Count(
            "memberships",
            _filter=Q(
                memberships__organization__memberships__pk=uuid,
                memberships__is_admin=True,
            ),
        ),
    ]
    return await resolver.delete_item(auth, uuid, write_perm_subqueries)
