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
from app.dependencies.organization import get_current_task

from app.models.user import User
from app.models.task import Task

from app.schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentUpdate,
    TaskCommentResponse,
    PaginatedTaskCommentsResponse,
)

from app.services.task_comment import (
    create_new_comment,
    get_task_comments,
    edit_comment,
    remove_comment,
)


router = APIRouter(
    prefix=(
        "/organizations/"
        "{organization_id}/projects/"
        "{project_id}/tasks/"
        "{task_id}/comments"
    ),
    tags=["Task Comments"],
)


@router.post(
    "",
    response_model=TaskCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    data: TaskCommentCreate,
    db: Session = Depends(get_db),
    task: Task = Depends(get_current_task),
    current_user: User = Depends(
        require_permission(
            "tasks.update"
        )
    ),
):
    """
    Create a task comment.

    The dependency chain ensures that:
    - the organization exists,
    - the current user belongs to the organization,
    - the project exists within the organization,
    - the task exists within the project.
    """

    try:
        return create_new_comment(
            db,
            task,
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
    response_model=PaginatedTaskCommentsResponse,
)
def list_comments_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    task: Task = Depends(get_current_task),
    current_user: User = Depends(
        require_permission(
            "tasks.view"
        )
    ),
):
    """
    List comments for a task.

    The dependency chain ensures that:
    - the organization exists,
    - the current user belongs to the organization,
    - the project exists within the organization,
    - the task exists within the project.
    """

    try:
        return get_task_comments(
            db,
            task,
            skip,
            limit,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/{comment_id}",
    response_model=TaskCommentResponse,
)
def update_comment_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    comment_id: UUID,
    data: TaskCommentUpdate,
    db: Session = Depends(get_db),
    task: Task = Depends(get_current_task),
    current_user: User = Depends(
        require_permission(
            "tasks.update"
        )
    ),
):
    """
    Update a task comment.

    The authenticated user may only update
    their own comment.
    """

    try:
        return edit_comment(
            db,
            task,
            comment_id,
            current_user.id,
            data,
        )

    except ValueError as error:

        if str(error) == "Comment not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{comment_id}",
)
def delete_comment_endpoint(
    organization_id: UUID,
    project_id: UUID,
    task_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    task: Task = Depends(get_current_task),
    current_user: User = Depends(
        require_permission(
            "tasks.update"
        )
    ),
):
    """
    Delete a task comment.

    The authenticated user may only delete
    their own comment.
    """

    try:
        remove_comment(
            db,
            task,
            comment_id,
            current_user.id,
        )

        return {
            "message": (
                "Comment deleted successfully"
            )
        }

    except ValueError as error:

        if str(error) == "Comment not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
