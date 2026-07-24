import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request tracing and response logging.

    Adds:
    - Request ID
    - Response timing
    - Response status logging
    """


    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        request_id = str(uuid.uuid4())

        start_time = time.perf_counter()

        request.state.request_id = request_id

        response = await call_next(request)

        process_time = (
            time.perf_counter() - start_time
        )

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s completed with %s in %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response