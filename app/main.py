from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router

from app.core.exceptions import EmailAlreadyRegistered


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

@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Welcome to PulseAPI🚀!",
    }