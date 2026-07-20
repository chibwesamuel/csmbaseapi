from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import EmailAlreadyRegistered

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.role_permissions import router as role_permissions_router
from app.api.v1.user_roles import router as user_roles_router
from app.api.v1.organizations import router as organizations_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.exception_handler(EmailAlreadyRegistered)
def email_exists_exception_handler(
    request: Request,
    exc: EmailAlreadyRegistered,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message
        },
    )


app.include_router(auth_router)

app.include_router(users_router)

app.include_router(roles_router)

app.include_router(permissions_router)

app.include_router(role_permissions_router)

app.include_router(user_roles_router)

app.include_router(organizations_router)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Welcome to PulseAPI🚀!",
    }