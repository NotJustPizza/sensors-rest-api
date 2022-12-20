from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["root"])


@router.get("/")
async def index():
    return JSONResponse("Welcome!")
