import json

from uuid import UUID

from app.core.redis import get_redis


TASK_CACHE_TTL = 300


def task_cache_key(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
) -> str:
    """
    Build the Redis cache key for a task response.
    """

    return (
        f"task:response:"
        f"{organization_id}:"
        f"{project_id}:"
        f"{task_id}"
    )


def get_cached_task(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
) -> dict | None:
    """
    Retrieve a cached task response.

    Returns None when the cache is unavailable
    or the key does not exist.
    """

    redis = get_redis()

    try:
        value = redis.get(
            task_cache_key(
                organization_id,
                project_id,
                task_id,
            )
        )

        if value is None:
            return None

        return json.loads(value)

    except Exception:
        return None


def cache_task(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    data: dict,
    expire: int = TASK_CACHE_TTL,
) -> bool:
    """
    Cache a task response.
    """

    redis = get_redis()

    try:
        redis.setex(
            task_cache_key(
                organization_id,
                project_id,
                task_id,
            ),
            expire,
            json.dumps(data),
        )

        return True

    except Exception:
        return False


def invalidate_task_cache(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
) -> bool:
    """
    Remove a task's cached response.
    """

    redis = get_redis()

    try:
        redis.delete(
            task_cache_key(
                organization_id,
                project_id,
                task_id,
            )
        )

        return True

    except Exception:
        return False
