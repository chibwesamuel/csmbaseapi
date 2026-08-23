import uuid

from app.services.task_cache import (
    cache_task,
    get_cached_task,
    invalidate_task_cache,
)


def test_task_cache_set_and_get():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()
    task_id = uuid.uuid4()

    data = {
        "id": str(task_id),
        "project_id": str(project_id),
        "organization_id": str(organization_id),
        "title": "CSMBaseAPI Task",
        "status": "todo",
    }

    assert cache_task(
        organization_id,
        project_id,
        task_id,
        data,
    ) is True

    assert get_cached_task(
        organization_id,
        project_id,
        task_id,
    ) == data

    invalidate_task_cache(
        organization_id,
        project_id,
        task_id,
    )


def test_task_cache_miss():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()
    task_id = uuid.uuid4()

    assert get_cached_task(
        organization_id,
        project_id,
        task_id,
    ) is None


def test_task_cache_invalidation():

    organization_id = uuid.uuid4()
    project_id = uuid.uuid4()
    task_id = uuid.uuid4()

    data = {
        "id": str(task_id),
        "project_id": str(project_id),
        "organization_id": str(organization_id),
        "title": "Test Task",
        "status": "todo",
    }

    cache_task(
        organization_id,
        project_id,
        task_id,
        data,
    )

    assert get_cached_task(
        organization_id,
        project_id,
        task_id,
    ) == data

    assert invalidate_task_cache(
        organization_id,
        project_id,
        task_id,
    ) is True

    assert get_cached_task(
        organization_id,
        project_id,
        task_id,
    ) is None