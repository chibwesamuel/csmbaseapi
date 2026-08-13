from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import EmailAlreadyRegistered
from app.core.responses import error_response


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

    return error_response(
        message=exc.message,
        status_code=400,
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
    """

    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code,
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
    """

    return error_response(
        message="Validation error",
        status_code=422,
        errors=exc.errors(),
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

    return error_response(
        message="Internal server error",
        status_code=500,
    )