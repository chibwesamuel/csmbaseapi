from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task


def create_task(
    db: Session,
    **kwargs,
) -> Task:
    """
    Create a task.
    """

    task = Task(**kwargs)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(
    db: Session,
    project_id: UUID,
    task_id: UUID,
) -> Task | None:
    """
    Retrieve a task belonging to a project.
    """

    return (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
            Task.id == task_id,
        )
        .first()
    )


def get_task_by_title(
    db: Session,
    project_id: UUID,
    title: str,
) -> Task | None:
    """
    Retrieve a task by title within a project.
    """

    return (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
            Task.title == title,
        )
        .first()
    )


def list_tasks(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
):
    """
    List tasks for a project with optional filters.
    """

    query = (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
        )
    )

    if status is not None:
        query = query.filter(
            Task.status == status
        )

    if priority is not None:
        query = query.filter(
            Task.priority == priority
        )

    if assigned_to is not None:
        query = query.filter(
            Task.assigned_to == assigned_to
        )

    total = query.count()

    tasks = (
        query.order_by(
            Task.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, tasks


def update_task(
    db: Session,
    task: Task,
    **kwargs,
) -> Task:
    """
    Update a task.
    """

    for key, value in kwargs.items():
        if value is not None:
            setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    db: Session,
    task: Task,
) -> bool:
    """
    Delete a task.
    """

    db.delete(task)
    db.commit()

    return True