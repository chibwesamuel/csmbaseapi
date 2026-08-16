from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project_member import ProjectMember
from app.models.user import User

from app.schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentUpdate,
)

from app.repositories.task_comment import (
    create_comment,
    get_comment,
    list_comments,
    update_comment,
    delete_comment,
)


def _get_task(
    db: Session,
    project_id: UUID,
    task_id: UUID,
) -> Task:
    """
    Retrieve a task belonging to the requested project.
    """

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.project_id == project_id,
        )
        .first()
    )

    if not task:
        raise ValueError(
            "Task not found"
        )

    return task


def create_new_comment(
    db: Session,
    project_id: UUID,
    task_id: UUID,
    user_id: UUID,
    data: TaskCommentCreate,
):
    """
    Create a new task comment.

    The task must belong to the requested project,
    and the user must be a member of that project.
    """

    task = _get_task(
        db,
        project_id,
        task_id,
    )

    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )

    if not membership:
        raise ValueError(
            "User is not a project member"
        )

    return create_comment(
        db,
        task_id=task.id,
        user_id=user_id,
        content=data.content,
    )


def get_task_comments(
    db: Session,
    project_id: UUID,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List comments for a task.

    The task must belong to the requested project.
    """

    _get_task(
        db,
        project_id,
        task_id,
    )

    total, comments = list_comments(
        db,
        task_id,
        skip,
        limit,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "comments": comments,
    }


def edit_comment(
    db: Session,
    project_id: UUID,
    task_id: UUID,
    comment_id: UUID,
    user_id: UUID,
    data: TaskCommentUpdate,
):
    """
    Update a comment.

    The task must belong to the requested project,
    the comment must belong to the requested task,
    and the user must own the comment.
    """

    _get_task(
        db,
        project_id,
        task_id,
    )

    comment = get_comment(
        db,
        comment_id,
        task_id,
    )

    if not comment:
        raise ValueError(
            "Comment not found"
        )

    if comment.user_id != user_id:
        raise ValueError(
            "You can only update your own comments"
        )

    return update_comment(
        db,
        comment,
        data.content,
    )


def remove_comment(
    db: Session,
    project_id: UUID,
    task_id: UUID,
    comment_id: UUID,
    user_id: UUID,
):
    """
    Delete a comment.

    The task must belong to the requested project,
    the comment must belong to the requested task,
    and the user must own the comment.
    """

    _get_task(
        db,
        project_id,
        task_id,
    )

    comment = get_comment(
        db,
        comment_id,
        task_id,
    )

    if not comment:
        raise ValueError(
            "Comment not found"
        )

    if comment.user_id != user_id:
        raise ValueError(
            "You can only delete your own comments"
        )

    return delete_comment(
        db,
        comment,
    )