from fastapi import Request

from app.core.exceptions import RateLimitExceeded
from app.services.cache import increment


def rate_limit(
    name: str,
    limit: int,
    window: int,
):
    """
    Create a FastAPI dependency that limits requests
    from the same client IP within a fixed time window.

    Redis failures fail open so that an unavailable Redis
    instance does not prevent authentication endpoints
    from functioning.
    """

    def dependency(
        request: Request,
    ):
        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        key = (
            f"rate_limit:{name}:{client_ip}"
        )

        count = increment(
            key,
            expire=window,
        )

        # Fail open if Redis is unavailable.
        if count is None:
            return None

        if count > limit:
            raise RateLimitExceeded(
                retry_after=window,
            )

        return None

    return dependency
