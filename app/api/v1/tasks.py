from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.organization import (
    get_current_project,
    get_current_task,
)
from app.dependencies.permissions import require_permission

from app.models.project import Project
from app.models.task import Task
from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    PaginatedTasksResponse,
)

from app.services.task import (
    create_new_task,
    get_tasks,
    get_single_task,
    edit_task,
    remove_task,
)

from app.services.task_cache import (
    cache_task,
    get_cached_task,
)

router = APIRouter(
    prefix=(
        "/organizations/"
        "{organization_id}/projects/"
        "{project_id}/tasks"
    ),
    tags=["Tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    organization_id: UUID,
    project_id: UUID,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_project: Project = Depends(
        get_current_project
    ),
    current_user: User = Depends(
        require_permission(
            "tasks.create"
        )
    ),
):
    """
    Create a task inside the current project.

    The current project dependency ensures that:
    - the organization exists,
    - the current user belongs to the organization,
    - the project exists,
    - the project belongs to the organization.
    """

    try:
        return create_new_task(
            db,
            current_project,
            current_user.id,
            data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "",
    response_model=PaginatedTasksResponse,
)
def list_project_tasks(
    organization_id: UUID,
    project_id: UUID,
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
    db: Session = Depends(get_db),
    current_project: Project = Depends(
        get_current_project
    ),
    current_user: User = Depends(
        require_permission(
            "tasks.view"
        )
    ),
):
    """
    List tasks belonging to the current project.
    """

    return get_tasks(
        db,
        current_project.id,
        skip,
        limit,
        status,
        priority,
        assigned_to,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    current_project: Project = Depends(
        get_current_project
    ),
    task: Task = Depends(
        get_current_task
    ),
    current_user: User = Depends(
        require_permission(
            "tasks.view"
        )
    ),
):
    """
    Retrieve a task from the current project.

    Authorization and task validation are completed
    before consulting the response cache.
    """

    cached = get_cached_task(
        current_project.organization_id,
        current_project.id,
        task_id,
    )

    if cached is not None:
        return cached

    response = TaskResponse.model_validate(
        task
    )

    data = response.model_dump(
        mode="json"
    )

    cache_task(
        current_project.organization_id,
        current_project.id,
        task_id,
        data,
    )

    return response


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_project: Project = Depends(
        get_current_project
    ),
    task: Task = Depends(
        get_current_task
    ),
    current_user: User = Depends(
        require_permission(
            "tasks.update"
        )
    ),
):
    """
    Update a task belonging to the current project.

    The get_current_task dependency validates
    the task before the service is called.
    """

    try:
        return edit_task(
            db,
            current_project,
            task,
            data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{task_id}",
)
def delete_task_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    current_project: Project = Depends(
        get_current_project
    ),
    task: Task = Depends(
        get_current_task
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "tasks.delete"
        )
    ),
):
    """
    Delete a task belonging to the current project.

    The get_current_task dependency validates
    the task before deletion.
    """

    remove_task(
        db,
        current_project,
        task,
    )

    return {
        "message": "Task deleted successfully"
    }
