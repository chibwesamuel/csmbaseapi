import json

from uuid import UUID

from app.core.redis import get_redis


PROJECT_CACHE_TTL = 300


def project_cache_key(
    organization_id: UUID,
    project_id: UUID,
) -> str:
    """
    Build the Redis cache key for a project response.
    """

    return (
        f"project:response:"
        f"{organization_id}:"
        f"{project_id}"
    )


def get_cached_project(
    organization_id: UUID,
    project_id: UUID,
) -> dict | None:
    """
    Retrieve a cached project response.

    Returns None when the cache is unavailable
    or the key does not exist.
    """

    redis = get_redis()

    try:
        value = redis.get(
            project_cache_key(
                organization_id,
                project_id,
            )
        )

        if value is None:
            return None

        return json.loads(value)

    except Exception:
        return None


def cache_project(
    organization_id: UUID,
    project_id: UUID,
    data: dict,
    expire: int = PROJECT_CACHE_TTL,
) -> bool:
    """
    Cache a project response.
    """

    redis = get_redis()

    try:
        redis.setex(
            project_cache_key(
                organization_id,
                project_id,
            ),
            expire,
            json.dumps(data),
        )

        return True

    except Exception:
        return False


def invalidate_project_cache(
    organization_id: UUID,
    project_id: UUID,
) -> bool:
    """
    Remove a project's cached response.
    """

    redis = get_redis()

    try:
        redis.delete(
            project_cache_key(
                organization_id,
                project_id,
            )
        )

        return True

    except Exception:
        return False
