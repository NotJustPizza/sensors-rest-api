from fastapi import FastAPI
from fastapi_pagination import add_pagination
from tortoise.contrib.fastapi import register_tortoise
from .settings import Settings
from .dependencies import get_settings
from .routers import routers
from .models import db_models
from .models.user import User


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="SensorsAPI",
        description="REST API used to store data from your sensors",
        version="0.0.1",
        license_info={"name": "All rights reserved!"},
    )

    # Ref: https://fastapi.tiangolo.com/advanced/settings/#settings-and-testing
    app.dependency_overrides[get_settings] = lambda: settings

    for router in routers:
        app.include_router(router)

    add_pagination(app)

    register_tortoise(
        app,
        db_url=settings.db_url,
        modules={"models": db_models},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    # Tortoise ORM has to be registered first
    @app.on_event("startup")
    async def create_admin_user():
        await User.update_or_create(
            defaults={"password": settings.admin_pass, "is_admin": True},
            email="admin@example.com",
        )

    return app
