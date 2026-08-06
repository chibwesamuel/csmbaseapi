from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project_member import ProjectMember
from app.models.user import User
from app.models.task_comment import TaskComment

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


def create_new_comment(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    data: TaskCommentCreate,
):
    """
    Create a new task comment.
    """

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
        )
        .first()
    )

    if not task:
        raise ValueError(
            "Task not found"
        )

    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == task.project_id,
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
        task_id=task_id,
        user_id=user_id,
        content=data.content,
    )


def get_task_comments(
    db: Session,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List comments for a task.
    """

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


def get_single_comment(
    db: Session,
    comment_id: UUID,
):
    """
    Retrieve one comment.
    """

    return get_comment(
        db,
        comment_id,
    )


def edit_comment(
    db: Session,
    comment_id: UUID,
    user_id: UUID,
    data: TaskCommentUpdate,
):
    """
    Update a comment.
    """

    comment = get_comment(
        db,
        comment_id,
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
    comment_id: UUID,
    user_id: UUID,
):
    """
    Delete a comment.
    """

    comment = get_comment(
        db,
        comment_id,
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