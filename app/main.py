from fastapi import FastAPI
from fastapi_pagination import add_pagination
from tortoise.contrib.fastapi import register_tortoise
from .routers import routers

app = FastAPI(
    title="SensorsAPI",
    description="REST API used to store data from your sensors",
    version="0.0.1",
    license_info={"name": "All rights reserved!"},
)


for router in routers:
    app.include_router(router)

db_models = [
    "app.models.user",
]

register_tortoise(
    app,
    db_url="sqlite://:memory:",
    modules={"models": db_models},
    generate_schemas=True,
    add_exception_handlers=True,
)

add_pagination(app)
