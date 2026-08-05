from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.dependencies.permissions import require_permission

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


router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/tasks",
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
    current_user: User = Depends(
        require_permission(
            "tasks.create"
        )
    ),
):
    """
    Create a task.
    """

    try:
        return create_new_task(
            db,
            project_id,
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
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "tasks.view"
        )
    ),
):
    """
    List project tasks.
    """

    return get_tasks(
        db,
        project_id,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "tasks.view"
        )
    ),
):
    """
    Retrieve a single task.
    """

    task = get_single_task(
        db,
        project_id,
        task_id,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


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
    current_user: User = Depends(
        require_permission(
            "tasks.update"
        )
    ),
):
    """
    Update a task.
    """

    try:
        return edit_task(
            db,
            project_id,
            task_id,
            data,
        )

    except ValueError as error:

        if str(error) == "Task not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )

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
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "tasks.delete"
        )
    ),
):
    """
    Delete a task.
    """

    try:

        remove_task(
            db,
            project_id,
            task_id,
        )

        return {
            "message": "Task deleted successfully"
        }

    except ValueError as error:

        if str(error) == "Task not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )