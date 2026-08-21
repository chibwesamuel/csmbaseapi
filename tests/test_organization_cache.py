import uuid

from app.services.organization_cache import (
    cache_organization,
    get_cached_organization,
    invalidate_organization_cache,
)


def test_organization_cache_set_and_get():

    organization_id = uuid.uuid4()

    data = {
        "id": str(organization_id),
        "name": "CSMBaseAPI",
        "slug": "csmbaseapi",
    }

    assert cache_organization(
        organization_id,
        data,
    ) is True

    assert get_cached_organization(
        organization_id
    ) == data

    invalidate_organization_cache(
        organization_id
    )


def test_organization_cache_miss():

    organization_id = uuid.uuid4()

    assert get_cached_organization(
        organization_id
    ) is None


def test_organization_cache_invalidation():

    organization_id = uuid.uuid4()

    data = {
        "id": str(organization_id),
        "name": "Test Organization",
        "slug": "test-organization",
    }

    cache_organization(
        organization_id,
        data,
    )

    assert get_cached_organization(
        organization_id
    ) == data

    assert invalidate_organization_cache(
        organization_id
    ) is True

    assert get_cached_organization(
        organization_id
    ) is None