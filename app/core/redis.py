from redis import Redis

from app.core.config import settings


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def get_redis() -> Redis:
    """
    Return the shared Redis client.
    """

    return redis_client


def redis_is_available() -> bool:
    """
    Check whether Redis is reachable.

    Returns False instead of raising if Redis
    is unavailable.
    """

    try:
        return bool(redis_client.ping())

    except Exception:
        return False