import uuid

from app.core.redis import redis_is_available
from app.services.cache import (
    cache_exists,
    delete_cache,
    get_cache,
    increment,
    set_cache,
)


def test_redis_is_available():

    assert redis_is_available() is True


def test_cache_set_and_get():

    key = f"test:cache:{uuid.uuid4()}"

    value = {
        "name": "CSMBaseAPI",
        "version": "1.0.0",
    }

    assert set_cache(
        key,
        value,
    ) is True

    assert get_cache(key) == value

    delete_cache(key)


def test_cache_exists():

    key = f"test:exists:{uuid.uuid4()}"

    assert set_cache(
        key,
        {"value": True},
    ) is True

    assert cache_exists(key) is True

    delete_cache(key)

    assert cache_exists(key) is False


def test_cache_delete():

    key = f"test:delete:{uuid.uuid4()}"

    set_cache(
        key,
        "temporary",
    )

    assert delete_cache(key) is True

    assert get_cache(key) is None


def test_cache_expiration():

    key = f"test:expire:{uuid.uuid4()}"

    assert set_cache(
        key,
        {"temporary": True},
        expire=1,
    ) is True

    assert get_cache(key) == {
        "temporary": True
    }

    delete_cache(key)


def test_increment():

    key = f"test:counter:{uuid.uuid4()}"

    assert increment(
        key,
        expire=60,
    ) == 1

    assert increment(key) == 2
    assert increment(key) == 3

    delete_cache(key)