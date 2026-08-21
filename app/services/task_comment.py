from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project_member import ProjectMember

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
    task: Task,
    user_id: UUID,
    data: TaskCommentCreate,
):
    """
    Create a new task comment.

    The task has already been validated by the
    get_current_task dependency.

    The user must also be a member of the
    project containing the task.
    """

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
        task_id=task.id,
        user_id=user_id,
        content=data.content,
    )


def get_task_comments(
    db: Session,
    task: Task,
    skip: int = 0,
    limit: int = 10,
):
    """
    List comments for a task.

    The task has already been validated by the
    get_current_task dependency.
    """

    total, comments = list_comments(
        db,
        task.id,
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
    task: Task,
    comment_id: UUID,
    user_id: UUID,
    data: TaskCommentUpdate,
):
    """
    Update a comment.

    The task has already been validated by the
    get_current_task dependency.

    The comment must belong to the requested task,
    and the user must own the comment.
    """

    comment = get_comment(
        db,
        comment_id,
        task.id,
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
    task: Task,
    comment_id: UUID,
    user_id: UUID,
):
    """
    Delete a comment.

    The task has already been validated by the
    get_current_task dependency.

    The comment must belong to the requested task,
    and the user must own the comment.
    """

    comment = get_comment(
        db,
        comment_id,
        task.id,
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
