from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router

from app.api.v1.role_permissions import (
    router as role_permissions_router,
)

from app.api.v1.user_roles import (
    router as user_roles_router,
)

from app.api.v1.organizations import (
    router as organizations_router,
)

from app.api.v1.organization_members import (
    router as organization_members_router,
)

from app.api.v1.organization_invitations import (
    router as organization_invitations_router,
)

from app.api.v1.projects import (
    router as projects_router,
)

from app.api.v1.project_members import (
    router as project_members_router,
)

from app.api.v1.tasks import (
    router as tasks_router,
)


api_router = APIRouter()


api_router.include_router(auth_router)

api_router.include_router(users_router)

api_router.include_router(roles_router)

api_router.include_router(permissions_router)

api_router.include_router(role_permissions_router)

api_router.include_router(user_roles_router)

api_router.include_router(organizations_router)

api_router.include_router(organization_members_router)

api_router.include_router(
    organization_invitations_router
)

api_router.include_router(
    projects_router
)

api_router.include_router(
    project_members_router
)

api_router.include_router(tasks_router)