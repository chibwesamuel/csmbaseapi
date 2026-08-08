from fastapi import (
    FastAPI,
    Request,
    HTTPException,
)

from fastapi.exceptions import RequestValidationError

from strawberry.fastapi import GraphQLRouter

from app.core.config import settings

from app.core.exceptions import EmailAlreadyRegistered

from app.core.exception_handlers import (
    email_exists_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

from app.middleware.request_logging import RequestLoggingMiddleware

from app.api.v1.router import api_router

from app.graphql.schema import schema


# ==========================================================
# OpenAPI Metadata
# ==========================================================

tags_metadata = [
    {
        "name": "Authentication",
        "description": (
            "User registration, login, refresh token "
            "and logout operations."
        ),
    },
    {
        "name": "Users",
        "description": (
            "User account management and profile operations."
        ),
    },
    {
        "name": "Roles",
        "description": (
            "Role creation, assignment and management."
        ),
    },
    {
        "name": "Permissions",
        "description": (
            "Permission management and access control."
        ),
    },
    {
        "name": "Organization",
        "description": (
            "Organization creation and management."
        ),
    },
    {
        "name": "Organization Members",
        "description": (
            "Manage users inside organizations."
        ),
    },
    {
        "name": "GraphQL",
        "description": (
            "GraphQL query and mutation interface."
        ),
    },
    {
        "name": "System",
        "description": (
            "System health and API status endpoints."
        ),
    },
    {
    "name": "Project Members",
    "description": (
        "Manage users assigned to projects."
    ),
},
]


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# CSMBaseAPI

CSMBaseAPI is a modern, production-ready REST and GraphQL backend
built with FastAPI.

## Features

- JWT Authentication
- Refresh Token Authentication
- Role-Based Access Control (RBAC)
- Organization & Membership Management
- REST API
- GraphQL API
- PostgreSQL Database
- SQLAlchemy ORM
- Alembic Database Migrations
- Interactive Swagger Documentation

## Authentication

Most endpoints require authentication.

1. Login using **POST /auth/login**
2. Copy the returned **access_token**
3. Click **Authorize** in Swagger UI
4. Paste your token

Swagger automatically adds the required Bearer prefix.

## Authorization

Some endpoints require:

- Superuser privileges
- Organization owner privileges
- Organization administrator privileges

Authorization is enforced through FastAPI dependencies.
""",
    openapi_tags=tags_metadata,
    contact={
        "name": "CSMBaseAPI",
        "url": "https://github.com/chibwesamuel/pulseapi",
    },
    license_info={
        "name": "MIT",
    },
)


# ==========================================================
# Middleware
# ==========================================================

app.add_middleware(
    RequestLoggingMiddleware,
)


# ==========================================================
# Centralized Exception Handling
# ==========================================================

app.add_exception_handler(
    EmailAlreadyRegistered,
    email_exists_exception_handler,
)


app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)


app.add_exception_handler(
    Exception,
    global_exception_handler,
)


# ==========================================================
# REST API Routes
# ==========================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ==========================================================
# GraphQL
# ==========================================================

graphql_app = GraphQLRouter(
    schema,
)


app.include_router(
    graphql_app,
    prefix="/graphql",
    tags=["GraphQL"],
)


# ==========================================================
# System Endpoints
# ==========================================================


@app.get(
    "/",
    tags=["System"],
    summary="API status",
    description=(
        "Returns basic information about the running API service."
    ),
)
def root():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Welcome to CSMBaseAPI 🚀!",
    }



@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description=(
        "Returns the current health status of CSMBaseAPI."
    ),
)
def health_check():

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }