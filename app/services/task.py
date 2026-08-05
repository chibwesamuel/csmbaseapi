from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.models.project_member import ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate

from app.repositories.task import (
    create_task,
    get_task,
    get_task_by_title,
    list_tasks,
    update_task,
    delete_task,
)


def create_new_task(
    db: Session,
    project_id: UUID,
    created_by: UUID,
    data: TaskCreate,
):
    """
    Create a new task.
    """

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    existing = get_task_by_title(
        db,
        project_id,
        data.title,
    )

    if existing:
        raise ValueError(
            "A task with this title already exists"
        )

    if data.assigned_to:

        user = (
            db.query(User)
            .filter(User.id == data.assigned_to)
            .first()
        )

        if not user:
            raise ValueError(
                "Assigned user not found"
            )

        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == data.assigned_to,
            )
            .first()
        )

        if not membership:
            raise ValueError(
                "Assigned user is not a project member"
            )

    return create_task(
        db,
        project_id=project_id,
        created_by=created_by,
        assigned_to=data.assigned_to,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
    )


def get_tasks(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
):
    """
    List tasks.
    """

    total, tasks = list_tasks(
        db,
        project_id,
        skip,
        limit,
        status,
        priority,
        assigned_to,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": tasks,
    }


def get_single_task(
    db: Session,
    project_id: UUID,
    task_id: UUID,
):
    """
    Retrieve one task.
    """

    return get_task(
        db,
        project_id,
        task_id,
    )


def edit_task(
    db: Session,
    project_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
):
    """
    Update a task.
    """

    task = get_task(
        db,
        project_id,
        task_id,
    )

    if not task:
        raise ValueError("Task not found")

    if (
        data.title is not None
        and data.title != task.title
    ):
        duplicate = get_task_by_title(
            db,
            project_id,
            data.title,
        )

        if duplicate:
            raise ValueError(
                "A task with this title already exists"
            )

    if data.assigned_to is not None:

        user = (
            db.query(User)
            .filter(User.id == data.assigned_to)
            .first()
        )

        if not user:
            raise ValueError(
                "Assigned user not found"
            )

        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == data.assigned_to,
            )
            .first()
        )

        if not membership:
            raise ValueError(
                "Assigned user is not a project member"
            )

    return update_task(
        db,
        task,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assigned_to=data.assigned_to,
        due_date=data.due_date,
    )


def remove_task(
    db: Session,
    project_id: UUID,
    task_id: UUID,
):
    """
    Delete a task.
    """

    task = get_task(
        db,
        project_id,
        task_id,
    )

    if not task:
        raise ValueError("Task not found")

    return delete_task(
        db,
        task,
    )