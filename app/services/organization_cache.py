import json

from uuid import UUID

from app.core.redis import get_redis


ORGANIZATION_CACHE_TTL = 300


def organization_cache_key(
    organization_id: UUID,
) -> str:
    """
    Build the Redis cache key for an organization.
    """

    return (
        f"organization:response:{organization_id}"
    )


def get_cached_organization(
    organization_id: UUID,
) -> dict | None:
    """
    Retrieve a cached organization response.

    Returns None when the cache is unavailable
    or the key does not exist.
    """

    redis = get_redis()

    try:
        value = redis.get(
            organization_cache_key(
                organization_id
            )
        )

        if value is None:
            return None

        return json.loads(value)

    except Exception:
        return None


def cache_organization(
    organization_id: UUID,
    data: dict,
    expire: int = ORGANIZATION_CACHE_TTL,
) -> bool:
    """
    Cache an organization response.
    """

    redis = get_redis()

    try:
        redis.setex(
            organization_cache_key(
                organization_id
            ),
            expire,
            json.dumps(data),
        )

        return True

    except Exception:
        return False


def invalidate_organization_cache(
    organization_id: UUID,
) -> bool:
    """
    Remove an organization's cached response.
    """

    redis = get_redis()

    try:
        redis.delete(
            organization_cache_key(
                organization_id
            )
        )

        return True

    except Exception:
        return False