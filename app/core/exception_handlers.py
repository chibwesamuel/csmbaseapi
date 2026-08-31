from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger
from app.core.exceptions import AppException
from app.core.responses import error_response


# ==========================================================
# Application Exception Handler
# ==========================================================

async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """
    Convert application-level exceptions into
    standardized HTTP responses.
    """

    return error_response(
        message=exc.message,
        status_code=exc.status_code,
        headers=exc.headers,
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

    The client receives a generic error response while
    the complete exception and traceback are recorded
    in the application logs.
    """

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    logger.exception(
        "Unhandled exception [request_id=%s] %s %s",
        request_id,
        request.method,
        request.url.path,
    )

    return error_response(
        message="Internal server error",
        status_code=500,
        headers={
            "X-Request-ID": request_id,
        },
    )
