import uuid

from app.services.project_cache import (
    cache_project,
    get_cached_project,
    invalidate_project_cache,
)


def test_project_cache_set_and_get():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()

    data = {
        "id": str(project_id),
        "organization_id": str(organization_id),
        "name": "CSMBaseAPI",
        "slug": "csmbaseapi",
    }

    assert cache_project(
        organization_id,
        project_id,
        data,
    ) is True

    assert get_cached_project(
        organization_id,
        project_id,
    ) == data

    invalidate_project_cache(
        organization_id,
        project_id,
    )


def test_project_cache_miss():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()

    assert get_cached_project(
        organization_id,
        project_id,
    ) is None


def test_project_cache_invalidation():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()

    data = {
        "id": str(project_id),
        "organization_id": str(organization_id),
        "name": "Test Project",
        "slug": "test-project",
    }

    cache_project(
        organization_id,
        project_id,
        data,
    )

    assert get_cached_project(
        organization_id,
        project_id,
    ) == data

    assert invalidate_project_cache(
        organization_id,
        project_id,
    ) is True

    assert get_cached_project(
        organization_id,
        project_id,
    ) is None
