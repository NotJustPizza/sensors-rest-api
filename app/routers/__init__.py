from .root import router as root_router
from .users import router as users_router
from .ogranizations import router as organizations_router

routers = [root_router, users_router, organizations_router]
