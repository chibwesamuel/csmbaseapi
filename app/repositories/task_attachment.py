from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment


def create_attachment(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    file_name: str,
    file_path: str,
    file_type: str | None = None,
    file_size: int | None = None,
):
    """
    Create a task attachment.
    """

    attachment = TaskAttachment(
        task_id=task_id,
        uploaded_by=user_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment



def get_attachment(
    db: Session,
    attachment_id: UUID,
):
    """
    Retrieve a single attachment.
    """

    return (
        db.query(TaskAttachment)
        .filter(
            TaskAttachment.id == attachment_id,
        )
        .first()
    )



def list_attachments(
    db: Session,
    task_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """
    List attachments belonging to a task.
    """

    query = (
        db.query(TaskAttachment)
        .filter(
            TaskAttachment.task_id == task_id,
        )
    )

    total = query.count()

    attachments = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, attachments



def delete_attachment(
    db: Session,
    attachment: TaskAttachment,
):
    """
    Delete an attachment.
    """

    db.delete(attachment)
    db.commit()

    return attachment