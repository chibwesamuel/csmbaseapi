from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import EmailAlreadyRegistered


# ==========================================================
# Custom Exception Handlers
# ==========================================================


async def email_exists_exception_handler(
    request: Request,
    exc: EmailAlreadyRegistered,
):
    """
    Handle duplicate email registration attempts.
    """

    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
        },
    )


# ==========================================================
# FastAPI HTTP Exception Handler
# ==========================================================


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    """
    Handle FastAPI HTTP exceptions.

    Keeps FastAPI's default response contract:
    {
        "detail": "message"
    }
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
        headers=getattr(
            exc,
            "headers",
            None,
        ),
    )


# ==========================================================
# Validation Exception Handler
# ==========================================================


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handle request validation errors.

    Keeps FastAPI's validation format compatible
    with existing clients/tests.
    """

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
        },
    )


# ==========================================================
# Global Exception Handler
# ==========================================================


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Catch all unexpected exceptions.
    """

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )