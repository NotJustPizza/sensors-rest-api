from .actions import router as actions_router
from .ogranizations import router as organizations_router
from .projects import router as projects_router
from .users import router as users_router

resource_routers = (users_router, organizations_router, projects_router)
routers = (actions_router,) + resource_routers
