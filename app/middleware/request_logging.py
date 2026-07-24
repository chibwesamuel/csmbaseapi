import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming HTTP requests
    and their response times.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            "%s %s completed with %s in %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response