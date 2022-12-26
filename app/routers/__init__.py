from .root import router as root_router
from .users import router as users_router
from .ogranizations import router as organizations_router


resource_routers = (users_router, organizations_router)
routers = (root_router,) + resource_routers
