import json

from typing import Any

from app.core.redis import get_redis


def set_cache(
    key: str,
    value: Any,
    expire: int | None = None,
) -> bool:
    """
    Store a value in Redis.

    Complex Python values are serialized as JSON.
    """

    redis = get_redis()

    try:
        serialized = json.dumps(value)

        if expire is not None:
            redis.setex(
                key,
                expire,
                serialized,
            )

        else:
            redis.set(
                key,
                serialized,
            )

        return True

    except Exception:
        return False


def get_cache(
    key: str,
) -> Any | None:
    """
    Retrieve a cached value from Redis.
    """

    redis = get_redis()

    try:
        value = redis.get(key)

        if value is None:
            return None

        return json.loads(value)

    except Exception:
        return None


def delete_cache(
    key: str,
) -> bool:
    """
    Delete a cached value.
    """

    redis = get_redis()

    try:
        redis.delete(key)

        return True

    except Exception:
        return False


def cache_exists(
    key: str,
) -> bool:
    """
    Check whether a cache key exists.
    """

    redis = get_redis()

    try:
        return bool(
            redis.exists(key)
        )

    except Exception:
        return False


def increment(
    key: str,
    amount: int = 1,
    expire: int | None = None,
) -> int | None:
    """
    Atomically increment a Redis counter.

    Optionally applies an expiration time.
    """

    redis = get_redis()

    try:
        value = redis.incrby(
            key,
            amount,
        )

        if expire is not None and value == amount:
            redis.expire(
                key,
                expire,
            )

        return value

    except Exception:
        return None