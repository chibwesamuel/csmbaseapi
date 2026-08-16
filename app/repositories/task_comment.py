from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task_comment import TaskComment


def create_comment(
    db: Session,
    **kwargs,
) -> TaskComment:
    """
    Create a task comment.
    """

    comment = TaskComment(**kwargs)

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comment(
    db: Session,
    comment_id: UUID,
    task_id: UUID,
) -> TaskComment | None:
    """
    Retrieve a comment belonging to a specific task.
    """

    return (
        db.query(TaskComment)
        .filter(
            TaskComment.id == comment_id,
            TaskComment.task_id == task_id,
        )
        .first()
    )


def list_comments(
    db: Session,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List comments belonging to a task.
    """

    query = (
        db.query(TaskComment)
        .filter(
            TaskComment.task_id == task_id,
        )
        .order_by(
            TaskComment.created_at.desc()
        )
    )

    total = query.count()

    comments = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, comments


def update_comment(
    db: Session,
    comment: TaskComment,
    content: str,
) -> TaskComment:
    """
    Update a comment.
    """

    comment.content = content

    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(
    db: Session,
    comment: TaskComment,
) -> bool:
    """
    Delete a comment.
    """

    db.delete(comment)
    db.commit()

    return True