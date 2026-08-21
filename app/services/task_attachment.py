from math import ceil
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project_member import ProjectMember

from app.schemas.task_attachment import (
    TaskAttachmentCreate,
)

from app.repositories.task_attachment import (
    create_attachment,
    get_attachment,
    list_attachments,
    delete_attachment,
)


def create_new_attachment(
    db: Session,
    task: Task,
    user_id: UUID,
    data: TaskAttachmentCreate,
):
    """
    Create a new task attachment.

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

    return create_attachment(
        db,
        task_id=task.id,
        user_id=user_id,
        file_name=data.file_name,
        file_path=data.file_path,
        file_type=data.file_type,
        file_size=data.file_size,
    )


def get_task_attachments(
    db: Session,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List attachments for a task.
    """

    total, attachments = list_attachments(
        db,
        task_id,
        skip,
        limit,
    )

    page = (skip // limit) + 1

    total_pages = (
        ceil(total / limit)
        if total
        else 1
    )

    return {
        "total": total,
        "meta": {
            "page": page,
            "page_size": limit,
            "total_items": total,
            "total_pages": total_pages,
        },
        "attachments": attachments,
    }


def get_single_attachment(
    db: Session,
    attachment_id: UUID,
):
    """
    Retrieve one attachment.
    """

    return get_attachment(
        db,
        attachment_id,
    )


def remove_attachment(
    db: Session,
    attachment_id: UUID,
    user_id: UUID,
):
    """
    Delete an attachment.

    Users may only delete attachments they uploaded.
    """

    attachment = get_attachment(
        db,
        attachment_id,
    )

    if not attachment:
        raise ValueError(
            "Attachment not found"
        )

    if attachment.uploaded_by != user_id:
        raise ValueError(
            "You can only delete your own attachments"
        )

    return delete_attachment(
        db,
        attachment,
    )
