from fastapi import FastAPI
from fastapi_pagination import add_pagination
from tortoise.contrib.fastapi import register_tortoise
from .routers import routers
from .settings import Settings

db_models = [
    "app.models.user",
]

# Workaround for db_url not working in tortoise initializer for pytest
# Ref: https://github.com/tortoise/tortoise-orm/issues/704
def create_app():
    settings = Settings()
    application = FastAPI(
        title="SensorsAPI",
        description="REST API used to store data from your sensors",
        version="0.0.1",
        license_info={"name": "All rights reserved!"},
    )
    for router in routers:
        application.include_router(router)

    register_tortoise(
        application,
        db_url=settings.db_url,
        modules={"models": db_models},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    add_pagination(application)
    return application


app = create_app()
