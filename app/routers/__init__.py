from .actions import router as actions_router
from .devices import router as devices_router
from .dimensions import router as dimensions_router
from .measures import router as measures_router
from .memberships import router as memberships_router
from .ogranizations import router as organizations_router
from .projects import router as projects_router
from .users import router as users_router

resource_routers = (
    devices_router,
    dimensions_router,
    measures_router,
    memberships_router,
    organizations_router,
    projects_router,
    users_router,
)
routers = (actions_router,) + resource_routers
