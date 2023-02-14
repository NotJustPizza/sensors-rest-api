from datetime import datetime, timedelta, timezone
from typing import List

from pytest import mark

from app.models import User

pytestmark = mark.anyio


async def test_user_update(users: List[User]):
    user = users[0]

    initial_created_at = user.created_at
    initial_modified_at = user.modified_at
    initial_now = datetime.now(timezone.utc)
    delta = timedelta(milliseconds=50)

    assert initial_now - initial_created_at < delta
    assert initial_now - initial_modified_at < delta

    user.name = "lucian@example.com"
    await user.save()
    await user.refresh_from_db()

    assert initial_created_at == user.created_at
    assert initial_modified_at < user.modified_at
